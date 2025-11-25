import google.generativeai as genai
from app.core.config import settings
from supabase import create_client, Client
# CORRECT IMPORT (Matches ingest.py)
from langchain_huggingface import HuggingFaceEndpointEmbeddings

# 1. Configure Gemini Chat
try:
    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    print(f"Error configuring Gemini: {e}")
    model = None

# 2. Configure HF Cloud Embeddings
# This MUST match the settings in ingest.py
embeddings = HuggingFaceEndpointEmbeddings(
    model="sentence-transformers/all-MiniLM-L6-v2",
    task="feature-extraction",
    huggingfacehub_api_token=settings.HUGGINGFACEHUB_API_TOKEN,
)

# 3. Configure Supabase
supabase_client: Client = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_ANON_KEY
)

SYSTEM_PROMPT = """
You are 'Sahayogi,' a world-class Socratic AI Tutor for cybersecurity.
Rules:
1. DO NOT write code.
2. DO NOT give direct answers.
3. ONLY ask guiding questions.
4. Use the [PROVIDED CONTEXT] if relevant.
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


async def get_socratic_response(prompt: str, chat_history: list = []):
    if not model:
        return "AI model is not configured."

    try:
        # STEP A: Generate Embedding
        query_vector = embeddings.embed_query(prompt)

        # STEP B: Call Supabase
        rpc_response = supabase_client.rpc(
            "match_documents",
            {
                "query_embedding": query_vector,
                "match_count": 5,
                "filter": {}
            }
        ).execute()

        relevant_docs = rpc_response.data
        context = ""
        if relevant_docs:
            context = "\n---\n".join([doc['content'] for doc in relevant_docs])
        else:
            context = "No specific documentation found."

        history_str = "\n".join([f"{msg.get('role', 'user')}: {msg.get('content', '')}" for msg in chat_history])

        full_prompt = SYSTEM_PROMPT.format(
            context=context,
            history=history_str,
            question=prompt
        )

        response = await model.generate_content_async(full_prompt)
        return response.text

    except Exception as e:
        print(f"Error in get_socratic_response: {e}")
        return f"Error: {e}"