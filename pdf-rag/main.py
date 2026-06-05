from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from rag_pipeline import ask_question

app = FastAPI(
    title="PDF RAG Application",
    description="Answer questions based on a PDF document using RAG pipeline",
    version="1.0.0"
)

# Request model
class QuestionRequest(BaseModel):
    question: str

# Response model
class QuestionResponse(BaseModel):
    answer: str
    sources: list

@app.get("/")
def root():
    return {"message": "PDF RAG Application is running. Use POST /ask to ask questions."}

@app.post("/ask", response_model=QuestionResponse)
def ask(request: QuestionRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    try:
        response = ask_question(request.question)
        return QuestionResponse(
            answer=response["answer"],
            sources=response["sources"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))