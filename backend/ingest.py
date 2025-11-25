import os
import sys

# Add backend to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import SupabaseVectorStore
# CORRECT IMPORT: Use the new Endpoint class
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from supabase import create_client, Client
from app.core.config import settings

supabase_admin_client: Client = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_SERVICE_ROLE_KEY
)

# NEW CONFIGURATION:
# - Use 'model' instead of 'model_name'
# - Use 'huggingfacehub_api_token' instead of 'api_key'
embeddings = HuggingFaceEndpointEmbeddings(
    model="sentence-transformers/all-MiniLM-L6-v2",
    task="feature-extraction",
    huggingfacehub_api_token=settings.HUGGINGFACEHUB_API_TOKEN,
)

vector_store = SupabaseVectorStore(
    client=supabase_admin_client,
    table_name="documents",
    query_name="match_documents",
    embedding=embeddings
)


def run_ingestion():
    print("Starting document ingestion with Hugging Face Cloud...")
    doc_directory = './docs'

    try:
        raw_docs = []
        for filename in os.listdir(doc_directory):
            if filename.endswith('.pdf'):
                print(f"Loading {filename}...")
                loader = PyPDFLoader(os.path.join(doc_directory, filename))
                raw_docs.extend(loader.load())

        if not raw_docs:
            print("No PDF documents found.")
            return

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        docs = text_splitter.split_documents(raw_docs)
        print(f"\nLoaded {len(docs)} chunks. Uploading to Supabase...")

        # Batch upload
        vector_store.add_documents(docs)
        print("\nSuccess! All documents uploaded using HF Cloud.")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    run_ingestion()