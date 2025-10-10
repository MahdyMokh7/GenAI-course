# 🇮🇷 Iranian Meal Recommender Chatbot

A Streamlit web application that recommends **top 3 Iranian meals** based on user ingredients and preferences.
Built with **Python**, **LangChain**, and **Llama-3** models (via Hugging Face or OpenAI-compatible endpoints).

---

## Features

* Chatbot interface to recommend meals for **lunch or dinner**.
* Users can specify:

  * Important ingredients (partial list is fine)
  * Meal type (traditional vs fast-food)
  * Heaviness (light/heavy)
  * Base (rice, bread, other)
* If user provides very little info, a **random traditional Iranian meal** is recommended.
* Optional **3-step quick recipe** for each meal.
* Uses **Llama-3** language model for smart recommendations.

---

## 📂 Project Structure

```
iranian_meal_bot/
├── app.py                # Streamlit chatbot application
├── requirements.txt      # All Python dependencies
├── .env                  # Stores API keys and model info (NOT tracked by Git)
├── .gitignore            # Ensures .env and venv are ignored
└── venv/                 # Python virtual environment (optional)
```

---

## ⚙️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/MahdyMokh7/GenAI-course.git
cd iranian_meal_bot_01
```

### 2. Create a virtual environment

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project folder with your API keys. Example for **free Hugging Face usage**:

```bash
PROVIDER=huggingface
HUGGINGFACEHUB_API_TOKEN=hf_your_free_token_here
LLAMA_MODEL=meta-llama/Llama-3-7B-Instruct
```

> **Notes:**
>
> * Only use **one provider** at a time (`huggingface` or `openai_compatible`).
> * Do **not** commit `.env` to GitHub — it contains sensitive API keys.
> * You can have multiple `.env` files for different projects.

---

### 5. Run the app

```bash
streamlit run app.py
```

This will start the Streamlit interface. Open the URL shown in the terminal (usually `http://localhost:8501`) in your browser.

---

## 📝 Usage

1. Enter **important ingredients** (comma-separated, e.g., `egg, tomato, chicken`).
2. Select meal **time** (lunch/dinner/any).
3. Choose **cuisine type** (traditional/fast-food/any).
4. Select **heaviness** (heavy/light/any).
5. Choose **base** (rice/bread/other/any).
6. Optionally, check **“Include quick 3-step recipe/tips”**.
7. Click **Recommend meals**.

The chatbot will display top 3 meal recommendations based on your inputs.

---

## ⚠️ Notes

* Free-tier Hugging Face usage is recommended for testing; smaller models (7B) are faster and free.
* Each subfolder/project can have its own `.env` file. Git will ignore them if configured correctly (`**/.env`).
* For production, consider hosting the Llama model on a GPU server for speed.

---

## 📦 Dependencies

* Python 3.10–3.12
* streamlit==1.38.0
* langchain==0.2.11
* huggingface-hub==0.24.6
* openai==1.43.0 (optional)
* python-dotenv==1.0.1
* transformers==4.44.2
* torch==2.4.0
* numpy==1.26.4
* requests==2.32.3
* tqdm==4.66.5

Install with:

```bash
pip install -r requirements.txt
```

---

## 🔗 References

* [Streamlit Documentation](https://docs.streamlit.io/)
* [LangChain Documentation](https://www.langchain.com/docs/)
* [Hugging Face Hub](https://huggingface.co/models)
