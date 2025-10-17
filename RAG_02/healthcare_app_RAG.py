import openai
import weaviate
import json
from openai.embeddings_utils import get_embedding
from sklearn.metrics.pairwise import cosine_similarity
import tiktoken

# Configuration
OPENAI_API_KEY = 'your-openai-api-key'
WEAVIATE_URL = 'https://your-weaviate-instance.com'

# Initialize Weaviate Client
client = weaviate.Client(WEAVIATE_URL)

# Initialize OpenAI Client
openai.api_key = OPENAI_API_KEY

# Define constants
MAX_TOKENS = 1500
EMBEDDING_MODEL = 'text-embedding-ada-002'  # OpenAI's embedding model
LLM_MODEL = 'gpt-4'  # OpenAI's language generation model
CHUNK_SIZE = 1000  # Maximum token size per document chunk

# Function to encode text into embeddings
def encode_text(text: str):
    return get_embedding(text, model=EMBEDDING_MODEL)

# Function to retrieve similar documents from Weaviate
def retrieve_documents(query: str, top_k=10):
    query_embedding = encode_text(query)
    
    # Perform similarity search in Weaviate
    result = client.query.get("Document", ["content", "source"])\
        .with_near_vector({"vector": query_embedding})\
        .with_limit(top_k)\
        .do()

    # Extract and return relevant documents
    documents = []
    for doc in result["data"]["Get"]["Document"]:
        documents.append({
            "content": doc["content"],
            "source": doc["source"]
        })
    return documents

# Function to concatenate the retrieved document content
def build_context(documents):
    context = ""
    for doc in documents:
        context += f"Source: {doc['source']}\nContent: {doc['content']}\n\n"
    return context

# Function to generate answer using OpenAI GPT-4
def generate_answer(question: str, context: str):
    prompt = f"""
    You are a helpful healthcare assistant. Answer the following question based on the provided context. 
    If the context doesn't contain enough information, state "I do not know."

    Context:
    {context}

    Question:
    {question}

    Answer:
    """
    
    response = openai.Completion.create(
        model=LLM_MODEL,
        prompt=prompt,
        max_tokens=MAX_TOKENS,
        temperature=0.5
    )
    
    return response.choices[0].text.strip()

# Ingest and store documents into Weaviate
def ingest_documents(documents):
    for doc in documents:
        content = doc['content']
        source = doc['source']
        embedding = encode_text(content)
        
        # Insert document into Weaviate
        client.data_object.create(
            data_object={"content": content, "source": source},
            class_name="Document",
            vector=embedding
        )

# Sample healthcare documents for ingestion
healthcare_docs = [
    {"content": "Diabetes is a chronic disease where the body is unable to regulate blood sugar levels.", "source": "Diabetes Overview"},
    {"content": "Hypertension, or high blood pressure, is a common cardiovascular condition that can lead to heart disease.", "source": "Hypertension Overview"},
    {"content": "COVID-19 vaccines are effective at preventing severe illness, hospitalization, and death.", "source": "COVID-19 Vaccine Efficacy"},
    {"content": "Antibiotic resistance occurs when bacteria evolve to resist the effects of drugs.", "source": "Antibiotic Resistance"},
    {"content": "Asthma is a chronic disease that affects the airways in the lungs, causing difficulty in breathing.", "source": "Asthma Overview"},
    {"content": "The flu (influenza) is a viral infection that attacks the respiratory system.", "source": "Influenza Overview"},
    {"content": "Heart disease refers to a range of conditions that affect the heart's structure and function.", "source": "Heart Disease Overview"},
    {"content": "Cancer occurs when cells in the body begin to grow uncontrollably, forming tumors.", "source": "Cancer Overview"},
    {"content": "Alzheimer’s disease is a progressive neurological disorder that causes memory loss and cognitive decline.", "source": "Alzheimer's Disease Overview"},
    {"content": "Osteoarthritis is the most common form of arthritis, causing joint pain and stiffness.", "source": "Osteoarthritis Overview"},
    {"content": "Chronic obstructive pulmonary disease (COPD) is a lung condition that causes breathing difficulties.", "source": "COPD Overview"},
    {"content": "Inflammatory bowel disease (IBD) is a group of disorders that cause chronic inflammation in the digestive tract.", "source": "IBD Overview"},
    {"content": "Epilepsy is a neurological disorder characterized by recurrent seizures.", "source": "Epilepsy Overview"},
    {"content": "HIV (Human Immunodeficiency Virus) attacks the immune system, potentially leading to AIDS.", "source": "HIV Overview"},
    {"content": "Multiple sclerosis (MS) is a disease where the immune system attacks the nervous system.", "source": "Multiple Sclerosis Overview"},
    {"content": "Parkinson's disease is a progressive neurological disorder that affects movement and coordination.", "source": "Parkinson's Disease Overview"},
    {"content": "Obesity is a medical condition characterized by excessive body fat that increases the risk of various diseases.", "source": "Obesity Overview"},
    {"content": "Tuberculosis (TB) is a bacterial infection that primarily affects the lungs, but can affect other parts of the body.", "source": "Tuberculosis Overview"},
    {"content": "Stroke occurs when the blood supply to part of the brain is interrupted, causing brain damage.", "source": "Stroke Overview"},
    {"content": "Chronic kidney disease (CKD) is the gradual loss of kidney function over time.", "source": "Chronic Kidney Disease Overview"},
    {"content": "Cystic fibrosis is a genetic disorder that affects the lungs, pancreas, and other organs.", "source": "Cystic Fibrosis Overview"},
    {"content": "Sickle cell disease is a genetic condition that causes abnormal red blood cells that can lead to blockages in blood vessels.", "source": "Sickle Cell Disease Overview"},
    {"content": "Hepatitis is an inflammation of the liver, often caused by viral infections.", "source": "Hepatitis Overview"},
    {"content": "Mental health disorders, such as depression and anxiety, are common and can affect a person's thoughts, emotions, and behavior.", "source": "Mental Health Overview"},
    {"content": "Pneumonia is an infection that causes inflammation in the air sacs of the lungs, leading to breathing difficulties.", "source": "Pneumonia Overview"},
    {"content": "Atherosclerosis is a condition where plaque builds up inside the arteries, increasing the risk of heart attack and stroke.", "source": "Atherosclerosis Overview"},
    {"content": "Rheumatoid arthritis is an autoimmune disease that causes inflammation in the joints.", "source": "Rheumatoid Arthritis Overview"},
    {"content": "SARS (Severe Acute Respiratory Syndrome) is a viral respiratory illness caused by a coronavirus.", "source": "SARS Overview"},
    {"content": "Chikungunya is a viral disease transmitted by mosquitoes, causing fever and joint pain.", "source": "Chikungunya Overview"}
]


# Ingest documents
ingest_documents(healthcare_docs)

# Main function to handle user query and provide RAG-based answer
def main():
    print("Welcome to the Healthcare Query System powered by Retrieval-Augmented Generation (RAG).")
    
    # Get user query
    user_query = input("Please enter your healthcare-related question: ")

    # Retrieve top documents based on the query
    documents = retrieve_documents(user_query)

    if not documents:
        print("Sorry, no relevant documents found.")
        return

    # Build context for the LLM
    context = build_context(documents)
    
    # Generate answer from the LLM using retrieved context
    answer = generate_answer(user_query, context)

    print("\nGenerated Answer:")
    print(answer)

if __name__ == "__main__":
    main()
