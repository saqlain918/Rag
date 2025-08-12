# app/rag/main.py - Clean version with only necessary endpoints
from fastapi import FastAPI
from app.rag.router import router

app = FastAPI(
    title="RAG API",
    description="RAG Application with JSON Responses",
    version="1.0.0"
)

# Include the router with only /upload and /ask endpoints
app.include_router(router)

@app.get("/")
def root():
    return {"message": "RAG API is running"}