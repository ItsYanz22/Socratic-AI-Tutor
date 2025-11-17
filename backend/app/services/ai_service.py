import google.generativeai as genai
from app.core.config import settings
from supabase import create_client, Client

# --- NEW IMPORTS ---
from langchain_community.vectorstores import SupabaseVectorStore
from langchain_huggingface import HuggingFaceEmbeddings

# --- 1. CONFIGURE CLIENTS ---

# Configure the Gemini client
try:
    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    print(f"Error configuring Gemini: {e}")
    model = None

# Configure free, local embeddings (must match ingest.py)
model_name = "sentence-transformers/all-MiniLM-L6-v2"
model_kwargs = {'device': 'cpu'}  # Use CPU
embeddings = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs
)

# Configure Supabase client (this one can be public for read-only search)
supabase_client: Client = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_ANON_KEY  # Use the ANON key for public read access
)

# Configure the Vector Store (for *retrieving* data)
vector_store = SupabaseVectorStore(
    client=supabase_client,
    table_name="documents",  # Must match your ingest.py table
    query_name="match_documents",  # Must match your ingest.py query
    embedding=embeddings
)

# --- 2. THE "SOUL" OF OUR AI (UPGRADED) ---
SYSTEM_PROMPT = """
You are 'Sahayogi,' a world-class Socratic AI Tutor for cybersecurity.
Your one and only goal is to help a student solve a problem *without ever giving them the answer*.
You must *only* respond with guiding questions.

RULES:
1.  **DO NOT** write code.
2.  **DO NOT** give direct, declarative answers.
3.  **ONLY** ask one or two guiding, open-ended questions in response.
4.  You *must* use the [PROVIDED CONTEXT] to inform your questions.
5.  If the context mentions 'scapy' or 'rdpcap', guide them towards it.
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

# --- 3. THE "RAG" ENABLED FUNCTION ---
async def get_socratic_response(prompt: str, chat_history: list = []):
    if not model:
        return "AI model is not configured. Please check API key."

    try:
        # --- THIS IS THE "R" (Retrieve) ---
        # First, retrieve relevant documents from our vector store
        print(f"RAG: Searching for context for: {prompt}")
        retriever = vector_store.as_retriever()
        relevant_docs = await retriever.ainvoke(prompt)

        # Format the context
        context = "\n---\n".join([doc.page_content for doc in relevant_docs])
        if not context:
            context = "No specific context found. Use general knowledge."

        # Format the history (This is Phase 3, so we implement it)
        history_str = "\n".join([f"{msg.get('role', 'user')}: {msg.get('content', '')}" for msg in chat_history])

        # --- THIS IS THE "A" (Augment) ---
        # Now, build the full prompt
        full_prompt = SYSTEM_PROMPT.format(
            context=context,
            history=history_str,
            question=prompt
        )

        # --- THIS IS THE "G" (Generate) ---
        response = await model.generate_content_async(full_prompt)
        print("RAG: Socratic response generated.")
        return response.text
    except Exception as e:
        print(f"Error in get_socratic_response: {e}")
        return f"Error connecting to AI model: {e}"