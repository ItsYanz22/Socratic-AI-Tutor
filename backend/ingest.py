import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import SupabaseVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from supabase import create_client, Client
from app.core.config import settings  # We'll reuse our config

# --- 1. CONFIGURE CLIENTS ---
# We need an admin client to write to the DB
supabase_admin_client: Client = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_SERVICE_ROLE_KEY
)

# --- THIS IS THE NEW CODE ---
# We are using a free, local model. It will download it the first time.
model_name = "sentence-transformers/all-MiniLM-L6-v2"
model_kwargs = {'device': 'cpu'} # Use CPU
embeddings = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs
)
# --- END OF NEW CODE ---

# Configure the Supabase Vector Store
vector_store = SupabaseVectorStore(
    client=supabase_admin_client,
    table_name="documents",  # This table will be created for you
    query_name="match_documents",
    embedding=embeddings
)


def run_ingestion():
    print("Starting document ingestion...")
    doc_directory = './docs'  # The folder with your PDFs

    # --- 2. LOAD & SPLIT DOCUMENTS ---
    try:
        raw_docs = []
        for filename in os.listdir(doc_directory):
            if filename.endswith('.pdf'):
                print(f"Loading {filename}...")
                loader = PyPDFLoader(os.path.join(doc_directory, filename))
                raw_docs.extend(loader.load())

        if not raw_docs:
            print("No PDF documents found in /docs folder.")
            return

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        docs = text_splitter.split_documents(raw_docs)
        print(f"Loaded and split {len(docs)} document chunks.")

        # --- 3. ADD TO VECTOR STORE ---
        vector_store.add_documents(docs)
        print("Successfully added documents to Supabase vector store.")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    # This makes the script runnable from the command line
    run_ingestion()