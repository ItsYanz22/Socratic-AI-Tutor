import google.generativeai as genai
from app.core.config import settings
from supabase import create_client, Client
from langchain_huggingface import HuggingFaceEmbeddings

# --- 1. CONFIGURE CLIENTS ---

# Configure Gemini
try:
    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel('models/gemini-2.0-flash')
except Exception as e:
    print(f"Error configuring Gemini: {e}")
    model = None

# Configure Embeddings (CPU)
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'}
)

# Configure Supabase
supabase_client: Client = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_ANON_KEY
)

# --- 2. THE SYSTEM PROMPT ---
SYSTEM_PROMPT = """
You are 'Sahayogi,' a world-class Socratic AI Tutor for cybersecurity.
Your goal is to help a student solve a problem *without* giving the answer.
Rules:
1. DO NOT write code.
2. DO NOT give direct answers.
3. ONLY ask guiding questions.
4. Use the [PROVIDED CONTEXT] if relevant.
5. If the context mentions 'scapy' or 'rdpcap', guide them towards it.
---
[PROVIDED CONTEXT]:
{context}
---
[CHAT HISTORY]:
{history}
---
[USER QUESTION]:
{question}
"""


# --- 3. THE "DIRECT RAG" FUNCTION ---
async def get_socratic_response(prompt: str, chat_history: list = []):
    if not model:
        return "AI model is not configured."

    try:
        # STEP A: Generate the Embedding Manually
        # We turn the user's question into numbers
        query_vector = embeddings.embed_query(prompt)

        # STEP B: Call Supabase Directly (The "Bypass")
        # We skip LangChain's buggy wrapper and talk straight to the DB
        # This calls the 'match_documents' SQL function we created
        rpc_response = supabase_client.rpc(
            "match_documents",
            {
                "query_embedding": query_vector,
                "match_count": 5,  # Get top 5 results
                "filter": {}
            }
        ).execute()

        # Format the results
        relevant_docs = rpc_response.data
        context = ""
        if relevant_docs:
            context = "\n---\n".join([doc['content'] for doc in relevant_docs])
        else:
            context = "No specific documentation found. Use general knowledge."

        # STEP C: Format History
        history_str = "\n".join([f"{msg.get('role', 'user')}: {msg.get('content', '')}" for msg in chat_history])

        # STEP D: Generate Response
        full_prompt = SYSTEM_PROMPT.format(
            context=context,
            history=history_str,
            question=prompt
        )

        response = await model.generate_content_async(full_prompt)
        return response.text

    except Exception as e:
        print(f"Error in get_socratic_response: {e}")
        return f"Error connecting to AI model: {e}"