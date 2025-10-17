# app.py
"""
Streamlit + LangChain Iranian Meal Recommender Chatbot (Llama-3 compatible)

Requirements (pip):
    pip install streamlit langchain huggingface_hub openai python-dotenv

How to configure:
- Option A (HuggingFace Hub):
    export HUGGINGFACEHUB_API_TOKEN="hf_...."
    export LLAMA_MODEL="meta-llama/Llama-3-70b-instruct"    # example model handle; replace with the exact model you have access to
    set PROVIDER="huggingface"

- Option B (OpenAI-compatible endpoint):
    export OPENAI_API_KEY="sk-..."
    export LLAMA_MODEL="llama-3"         # whatever your provider calls it
    set PROVIDER="openai_compatible"

Notes:
- Replace model names with the exact model ID you have access to.
- If using a self-hosted or other provider with an OpenAI-compatible API, set environment variables accordingly.
"""

import os
import random
import streamlit as st
from typing import Dict, Any, List

# LangChain LLM wrappers
from langchain import LLMChain, PromptTemplate
from langchain.memory import ConversationBufferMemory

from dotenv import load_dotenv
load_dotenv()

# We'll choose the wrapper depending on PROVIDER
PROVIDER = os.environ.get("PROVIDER", "huggingface")  # "huggingface" or "openai_compatible"

# Try to import LLM classes lazily so the app can show an error if missing
try:
    if PROVIDER == "huggingface":
        from langchain import HuggingFaceHub
    else:
        # for OpenAI-compatible endpoints (or OpenAI), use OpenAI from langchain
        from langchain import OpenAI
except Exception as e:
    # We'll handle missing libs at runtime in the UI
    pass

# ---------------------------
# Utilities & Constants
# ---------------------------

IRANIAN_MEALS = [
    # A small list of traditional iranian meals to pick randomly from when inputs are sparse
    {"name": "Ghormeh Sabzi", "type": "traditional", "base": "rice"},
    {"name": "Chelo Kebab", "type": "traditional", "base": "rice"},
    {"name": "Gheymeh", "type": "traditional", "base": "rice"},
    {"name": "Fesenjan", "type": "traditional", "base": "rice"},
    {"name": "Tahcheen", "type": "traditional", "base": "rice"},
    {"name": "Mirza Ghasemi", "type": "traditional", "base": "bread"},
    {"name": "Kookoo Sabzi", "type": "traditional", "base": "bread"},
    {"name": "Adas Polo", "type": "traditional", "base": "rice"},
    {"name": "Kashk-e Bademjan", "type": "traditional", "base": "bread"},
    {"name": "Zereshk Polo", "type": "traditional", "base": "rice"},
]

# A simple heuristic to measure "amount of info" supplied by user
def info_score(ingredients: str, meal_time: str, cuisine_type: str, heaviness: str, base: str) -> int:
    score = 0
    if ingredients and ingredients.strip():
        # count important ingredients words
        tokens = [t for t in ingredients.split(",") if t.strip()]
        score += min(len(tokens), 5)
    if meal_time and meal_time != "any":
        score += 1
    if cuisine_type and cuisine_type != "any":
        score += 1
    if heaviness and heaviness != "any":
        score += 1
    if base and base != "any":
        score += 1
    return score

# ---------------------------
# LLM Initialization
# ---------------------------

def init_llm():
    """
    Initialize a LangChain LLM instance depending on PROVIDER and environment variables.
    Returns a callable LLM object compatible with LangChain (with generate/text generation).
    """
    model_name = os.environ.get("LLAMA_MODEL", None)
    if PROVIDER == "huggingface":
        token = os.environ.get("HUGGINGFACEHUB_API_TOKEN", None)
        if not token or not model_name:
            raise RuntimeError("HuggingFace provider selected but HUGGINGFACEHUB_API_TOKEN or LLAMA_MODEL is not set.")
        # Use HuggingFaceHub LLM wrapper
        hf = HuggingFaceHub(repo_id=model_name, huggingfacehub_api_token=token, model_kwargs={"temperature":0.7, "max_new_tokens":512})
        return hf
    else:
        api_key = os.environ.get("OPENAI_API_KEY", None)
        if not api_key or not model_name:
            raise RuntimeError("OpenAI-compatible provider selected but OPENAI_API_KEY or LLAMA_MODEL is not set.")
        # Use OpenAI wrapper but set model to LLAMA_MODEL (useful if provider accepts that model name)
        # This will work for OpenAI or OpenAI-compatible endpoints if configured in your env.
        # LangChain's OpenAI class reads OPENAI_API_KEY automatically.
        openai_llm = OpenAI(model_name=model_name, temperature=0.7, max_tokens=512)
        return openai_llm

# ---------------------------
# Prompt Template
# ---------------------------

PROMPT_TEXT = """
You are an Iranian virtual chef assistant. The user will provide:
- important ingredients (not necessarily exhaustive),
- desired meal_time (lunch/dinner/any),
- cuisine_type (traditional/fast-food/any),
- heaviness (heavy/light/any),
- base (rice/bread/other/any).

Task:
1) Based on the inputs, produce a succinct list of the **top 3 recommended meals**, each with:
   - meal name (Iranian name preferred if applicable),
   - why it fits the user's ingredients and preferences (1-2 short sentences),
   - a very short 3-step recipe or quick tips for preparing it (each step 6-12 words).
2) If the user provided *very little* information (ingredients empty or info score low), choose a random Iranian traditional meal and explain briefly why it is recommended.
3) Be concise. Use bullet points or numbered list. No extra commentary.
4) If some requested option contradicts (e.g., asks "fast-food" but wants "rice-based heavy traditional stew"), prefer to ask the user to clarify only if the instructions are insufficient. Otherwise make a best-fitting recommendation and say "best fit" in parenthesis.

User inputs:
Ingredients: {ingredients}
Meal time: {meal_time}
Cuisine type: {cuisine_type}
Heaviness: {heaviness}
Base: {base}
Include_recipe: {include_recipe}

Output format:
- For each recommendation:
  1) Meal name — short parenthetical tags (base, heavy/light, traditional/fast-food)
     - Why: <one short sentence>
     - Recipe: 1) ... 2) ... 3) ...

If fallback (random): start with "FALLBACK RECOMMENDATION:" and then the same format for one meal.
"""

# few shot NOT still used
FEW_SHOT_EXAMPLES = """  
Example 1:
Ingredients: rice, saffron, chicken
Meal time: dinner
Cuisine type: traditional
Heaviness: heavy
Base: rice
Output:
1) Tahchin — (rice, heavy, traditional)
   - Why: Uses rice, saffron, and chicken perfectly.
   - Recipe: 1) Mix rice & saffron. 2) Add chicken. 3) Bake to golden crust.

Example 2:
Ingredients: eggplant, yogurt, mint
Meal time: lunch
Cuisine type: traditional
Heaviness: light
Base: bread
Output:
1) Kashk-e Bademjan — (bread, light, traditional)
   - Why: Fits eggplant and yogurt well.
   - Recipe: 1) Fry eggplant. 2) Add yogurt. 3) Serve with mint & bread.
"""

prompt = PromptTemplate(input_variables=["ingredients","meal_time","cuisine_type","heaviness","base","include_recipe"], template=PROMPT_TEXT)

# ---------------------------
# Streamlit UI
# ---------------------------

st.set_page_config(page_title="Iranian Meal Recommender (Llama-3)", layout="centered")

st.title("🇮🇷 Iranian Meal Recommender — Chatbot")
st.caption("Tell the bot important ingredients and preferences; it will recommend top-3 Iranian meals (Llama-3 compatible).")

with st.expander("Setup / Notes", expanded=False):
    st.write("""
    • This app expects a Llama-3 compatible model endpoint. Configure PROVIDER and credentials as described in the script header.  
    • PROVIDER environment variable: 'huggingface' or 'openai_compatible'.  
    • For minimal latency start with a small model or a hosted endpoint.
    """)

# Input area (left)
col1, col2 = st.columns([3,1])

with col1:
    ingredients = st.text_input("Important ingredients (comma-separated)", placeholder="egg, tomato, lentils, chicken, saffron ...")
    include_recipe = st.checkbox("Include quick 3-step recipe/tips?", value=True)
    user_message = st.text_area("Notes / extra preferences (optional)", height=80, placeholder="e.g. prefer spicy, avoid offal...")

with col2:
    meal_time = st.selectbox("Meal time", options=["any","lunch","dinner"])
    cuisine_type = st.selectbox("Cuisine type", options=["any","traditional","fast-food"])
    heaviness = st.selectbox("Heaviness", options=["any","heavy","light"])
    base = st.selectbox("Base", options=["any","rice","bread","other"])
    num_results = st.slider("Max recommendations to show", min_value=1, max_value=3, value=3)

generate_btn = st.button("Recommend meals")

# Conversation memory in session state
if "history" not in st.session_state:
    st.session_state.history = []

if generate_btn:
    # compute info score
    score = info_score(ingredients, meal_time, cuisine_type, heaviness, base)
    # fallback if too little info (e.g. score < 2)
    fallback = (score < 2)

    # prepare prompt inputs
    prompt_inputs = {
        "ingredients": ingredients or "",
        "meal_time": meal_time,
        "cuisine_type": cuisine_type,
        "heaviness": heaviness,
        "base": base,
        "include_recipe": str(include_recipe),
    }

    # If fallback: pick one random traditional meal and craft a short deterministic message to LLM
    if fallback:
        chosen = random.choice(IRANIAN_MEALS)
        # Create a small deterministic reply ourselves for immediate response, and also call LLM to get richer text if wanted.
        fallback_text = f"FALLBACK RECOMMENDATION:\n1) {chosen['name']} — ({chosen['base']}, traditional)\n   - Why: Classic, widely-liked, uses common pantry ingredients.\n   - Recipe: 1) Prepare ingredients. 2) Cook slowly. 3) Serve with rice or bread.\n\n(You provided very little info; showing a random Iranian traditional meal.)"
        # Store and show
        st.session_state.history.append({"role":"assistant","content":fallback_text})
        st.experimental_rerun()

    # If not fallback, call LLM
    try:
        with st.spinner("Contacting the LLM..."):
            llm = init_llm()
            chain = LLMChain(llm=llm, prompt=prompt, verbose=False, memory=ConversationBufferMemory())  # simple chain
            raw_response = chain.run(**prompt_inputs)
    except Exception as e:
        st.error(f"LLM initialization or call failed: {e}")
        st.stop()

    # Save conversation
    st.session_state.history.append({"role":"user","content":f"Ingredients: {ingredients} | meal_time: {meal_time} | cuisine_type: {cuisine_type} | heaviness: {heaviness} | base: {base}"})
    st.session_state.history.append({"role":"assistant","content":raw_response})

# Display history (latest first)
if st.session_state.history:
    st.markdown("### Conversation")
    for msg in reversed(st.session_state.history[-10:]):
        if msg["role"] == "user":
            st.markdown(f"**You:** {msg['content']}")
        else:
            st.markdown(f"**Bot:**\n{msg['content']}")

# Footer: quick local test helper
st.markdown("---")
st.markdown("**Quick local test suggestions:**")
st.markdown("- Try: `ingredients: egg, tomato` + `lunch` + `bread` -> Mirza Ghasemi / Kookoo Sabzi style suggestions.")
st.markdown("- Try: `ingredients: rice, saffron, chicken` + `dinner` + `traditional` -> Chelow Kebab or Tahchin suggestions.")