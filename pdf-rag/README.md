# PDF RAG Application

A PDF-based Retrieval-Augmented Generation (RAG) application that allows users to upload PDF documents and ask questions based on their content. Built with FastAPI, LangChain, ChromaDB, and Google Gemini.

---

## Project Overview

This application enables users to:
- Upload one or more PDF documents
- Process and store document embeddings in a vector database
- Ask natural language questions about the uploaded documents
- Receive accurate answers with source page references
- Switch between multiple documents using a simple UI

The system uses RAG (Retrieval-Augmented Generation) — it retrieves the most relevant chunks from the PDF and feeds them to an LLM to generate accurate, grounded answers.

---

## Tech Stack

| Component | Technology | Reason |
|---|---|---|
| Backend API | FastAPI | Fast, modern Python API framework |
| RAG Pipeline | LangChain | Built-in PDF loading, chunking, retrieval chains |
| PDF Loading | PyPDFLoader (LangChain) | Simple and reliable PDF text extraction |
| Embeddings | Google Gemini (gemini-embedding-exp-03-07) | High quality embeddings, same API key as LLM |
| Vector Database | ChromaDB | Local, persistent, zero infrastructure needed |
| LLM | Google Gemini (gemini-1.5-flash) | Fast, capable, free tier available |
| Frontend UI | Streamlit | Quick to build, Python-native chat interface |

---

## Tech Stack Used

- Python 3.11
- FastAPI
- LangChain + LangChain-Google-GenAI
- ChromaDB
- Google Gemini API (Embeddings + LLM)
- Streamlit
- PyPDF
- Uvicorn

---

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/pdf-rag.git
cd pdf-rag
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate       # Mac/Linux
venv\Scripts\activate          # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
Create a `.env` file in the root directory:
```
GOOGLE_API_KEY=your_gemini_api_key_here
```

Get your free Gemini API key at: https://aistudio.google.com

---

## Steps to Run the FastAPI Server

### Terminal 1 — Start FastAPI server
```bash
uvicorn main:app --reload
```
API will be available at: `http://127.0.0.1:8000`

Interactive API docs available at: `http://127.0.0.1:8000/docs`

### Terminal 2 — Start Streamlit UI
```bash
streamlit run app.py
```
UI will be available at: `http://localhost:8501`

---

## How to Use

1. Open `http://localhost:8501` in your browser
2. Upload a PDF using the sidebar
3. Click **Process PDF** and wait for embeddings to generate
4. Select the document from the dropdown in the sidebar
5. Type your question in the chat input
6. View the answer along with source page references

---

## API Endpoint Details

### Base URL
```
http://127.0.0.1:8000
```

### GET /
Health check — confirms the server is running.

**Response:**
```json
{
  "message": "PDF RAG Application is running. Use POST /ask to ask questions."
}
```

---

### GET /collections
Returns list of all processed documents available for querying.

**Response:**
```json
{
  "collections": ["document_one", "document_two"]
}
```

---

### POST /ask
Ask a question based on a specific document.

**Request Body:**
```json
{
  "question": "What is Retrieval-Augmented Generation?",
  "collection_name": "document"
}
```

**Response:**
```json
{
  "answer": "Retrieval-Augmented Generation (RAG) is a technique that combines information retrieval with text generation...",
  "sources": [1, 3, 5]
}
```

**Error Response (empty question):**
```json
{
  "detail": "Question cannot be empty"
}
```

---

## Example Questions and Responses

**Question 1:**
```json
{
  "question": "What are the three paradigms of RAG?",
  "collection_name": "document"
}
```
**Response:**
```json
{
  "answer": "The three paradigms of RAG are Naive RAG, Advanced RAG, and Modular RAG.",
  "sources": [1, 4, 16]
}
```

---

**Question 2:**
```json
{
  "question": "What are the limitations of Naive RAG?",
  "collection_name": "document"
}
```
**Response:**
```json
{
  "answer": "Naive RAG encounters notable drawbacks including retrieval challenges such as precision and recall issues, generation difficulties like hallucination, and augmentation hurdles when integrating retrieved information.",
  "sources": [3]
}
```

---

**Question 3:**
```json
{
  "question": "What is the difference between RAG and Fine-tuning?",
  "collection_name": "document"
}
```
**Response:**
```json
{
  "answer": "RAG excels in dynamic environments by offering real-time knowledge updates and effective utilization of external knowledge sources. Fine-tuning is more static, requiring retraining for updates but enabling deep customization of model behavior and style.",
  "sources": [5]
}
```

---

**Question 4:**
```json
{
  "question": "What evaluation metrics are used for RAG systems?",
  "collection_name": "document"
}
```
**Response:**
```json
{
  "answer": "RAG systems are evaluated using metrics such as Hit Rate, MRR, NDCG for retrieval quality, and BLEU, ROUGE, and Accuracy for generation quality. Quality scores include context relevance, answer faithfulness, and answer relevance.",
  "sources": [12, 13]
}
```

---

## Model Choices and Reasons

### Embedding Model — `gemini-embedding-exp-03-07`
- Uses the same Google API key as the LLM — no extra credentials needed
- Produces high quality semantic embeddings for accurate similarity search
- Free tier available via Google AI Studio

### LLM — `gemini-1.5-flash`
- Fast response times suitable for a chatbot experience
- Strong comprehension and summarization of retrieved context
- Generous free tier limits compared to other models
- Well supported natively in LangChain via `langchain-google-genai`

### Vector Database — ChromaDB
- Runs fully in-process with no external server required
- Automatically persists embeddings to disk
- Supports multiple named collections — one per uploaded document
- Native LangChain integration via `langchain-chroma`

### RAG Framework — LangChain
- Provides all required components out of the box — PDF loader, text splitter, retriever, and QA chain
- RetrievalQA chain with custom prompt template gives full control over the answer format
- Active community and well maintained integrations

---

## Project Structure

```
pdf-rag/
├── main.py              # FastAPI app with /ask and /collections endpoints
├── rag_pipeline.py      # LangChain RAG pipeline: retrieval, prompt, LLM
├── ingest.py            # PDF loading, chunking, embedding, ChromaDB storage
├── app.py               # Streamlit frontend UI with document selector
├── data/                # Uploaded PDF files (git ignored)
├── chroma_db/           # ChromaDB persistent vector store (git ignored)
├── requirements.txt     # Python dependencies
├── .env                 # API keys (git ignored)
└── README.md            # Project documentation
```

---

## Limitations

- **Rate limits:** Google Gemini free tier has limits (100 requests/min for embeddings). Large PDFs take several minutes to process due to batching with 65 second delays between batches.
- **Single document per query:** Each question is answered based on one selected document at a time. Cross-document querying is not supported.
- **No conversation memory:** The chatbot does not remember previous questions within a session. Each question is answered independently.
- **Text only:** Images, tables, charts, and diagrams inside PDFs are not extracted or understood. Only plain text content is processed.
- **English optimized:** The embedding model and LLM perform best with English language documents. Performance may vary for other languages.
- **Local storage only:** ChromaDB and uploaded PDFs are stored locally on disk. This setup is not suitable for multi-user cloud deployment without additional infrastructure changes.
- **API dependency:** The application requires a valid Google Gemini API key and an active internet connection to function.