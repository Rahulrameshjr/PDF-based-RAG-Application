import os
import time
import google.generativeai as genai
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
load_dotenv()

def ingest_pdf(pdf_path: str):
    print(f"Loading PDF from: {pdf_path}")
    
    # Step 1: Load PDF
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
                persist_directory="./chroma_db"
            )
        else:
            vectorstore.add_documents(batch)

        if i + BATCH_SIZE < len(chunks):
            print("Waiting 65 seconds to avoid rate limit...")
            time.sleep(65)

    print("Done! PDF ingested and stored in chroma_db/")
    return vectorstore

if __name__ == "__main__":
    ingest_pdf("data/Document.pdf")