import os
import time
import sys
import google.generativeai as genai
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
load_dotenv()

def ingest_pdf(pdf_path: str):
    print(f"Loading PDF from: {pdf_path}")

    # Use filename as collection name
    collection_name = os.path.splitext(os.path.basename(pdf_path))[0]
    collection_name = collection_name.replace(" ", "_").lower()

    loader = PyPDFLoader(pdf_path)
    pages = loader.load()
    print(f"Loaded {len(pages)} pages")

    # Step 2: Split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_documents(pages)
    print(f"Split into {len(chunks)} chunks")

    # Step 3: Generate embeddings in small batches with delay
    print("Generating embeddings and storing in ChromaDB...")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

    BATCH_SIZE = 50  # stay under 100/min limit
    vectorstore = None

    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i:i + BATCH_SIZE]
        print(f"Processing batch {i//BATCH_SIZE + 1} ({len(batch)} chunks)...")

        if vectorstore is None:
            vectorstore = Chroma.from_documents(
                documents=batch,
                embedding=embeddings,
                persist_directory="./chroma_db",
                collection_name=collection_name
            )
        else:
            vectorstore.add_documents(batch)

        if i + BATCH_SIZE < len(chunks):
            print("Waiting 65 seconds to avoid rate limit...")
            time.sleep(65)

    print(f"Done! PDF ingested under collection: {collection_name}")
    return collection_name

if __name__ == "__main__":
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else "data/Document.pdf"
    ingest_pdf(pdf_path)