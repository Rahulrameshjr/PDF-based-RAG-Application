import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_classic.chains import RetrievalQA

load_dotenv()

def load_rag_pipeline(collection_name: str):
    # Step 1: Load embeddings model
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

    # Step 2: Load existing ChromaDB
    vectorstore = Chroma(
        persist_directory="./chroma_db",
        embedding_function=embeddings,
        collection_name=collection_name
    )

    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.3
    )

    # Step 5: Create prompt template
    prompt_template = """
    You are a helpful assistant. Use the following context retrieved from a PDF document
    to answer the user's question accurately.
    If the answer is not found in the context, say "I could not find relevant information in the document."

    Context:
    {context}

    Question:
    {question}

    Answer:
    """

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )

    # Step 6: Build RetrievalQA chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt}
    )

    return qa_chain


def ask_question(question: str, collection_name: str):
    qa_chain = load_rag_pipeline(collection_name)
    result = qa_chain.invoke({"query": question})

    answer = result["result"]

    # Only return sources if relevant answer was found
    if "could not find" in answer.lower():
        sources = []
    else:
        sources = []
        for doc in result["source_documents"]:
            page = doc.metadata.get("page", "unknown")
            if isinstance(page, int):
                page = page + 1
            if page not in sources:
                sources.append(page)

    return {
        "answer": answer,
        "sources": sorted(sources) if sources else []
    }