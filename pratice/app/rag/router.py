# app/rag/router.py - Fixed version with only 2 endpoints
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
import shutil
import os

router = APIRouter()


# Request models
class QuestionRequest(BaseModel):
    question: str


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload and process PDF file for RAG"""
    try:
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)

        path = f"data/{file.filename}"
        with open(path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Process with embedder
        from app.rag_emb.embedding import PDFEmbedder
        embedder = PDFEmbedder()
        embedder.process_and_store()

        return {
            "message": f"{file.filename} uploaded and processed successfully.",
            "filename": file.filename,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ask")
async def ask_question(request: QuestionRequest):
    """Ask a question and get structured RAG response"""
    try:
        from app.rag.services import RAGService
        service = RAGService()
        result = service.answer_with_context(request.question)

        # Convert to dict if it's a pydantic model
        if hasattr(result, 'dict'):
            return result.dict()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))