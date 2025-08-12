# RAG (Retrieval-Augmented Generation) Project with Multiple Frontends

This project implements a RAG pipeline using FastAPI as the backend, Pinecone for vector storage, and Google Generative AI for embeddings and LLM responses.
It also provides three optional frontends for interacting with the RAG backend:
- Streamlit
- Chainlit
- Gradio

---
## Project Structure

```
pratice/
│
├── app/
│   ├── rag/                # Backend RAG logic
│   │   ├── main.py         # FastAPI entrypoint
│   │   ├── router.py       # API routes
│   │   ├── services.py     # RAG service handling retrieval + generation
│   │   ├── vector.py       # Vector & LLM handler classes
│   │
│   ├── rag_emb/            # PDF processing & embedding
│   │   └── embedding.py
│   │
│   ├── config.py           # API key & environment config loader
│
├── chainlit_app/
│   ├── .chainlit/
│   │   └── chainlit.md     # Chainlit UI markdown intro
│   └── rag_chainlit.py     # Chainlit frontend
│
├── gradio_app/
│   └── app.py              # Gradio frontend
│
├── streamlit_app/
│   └── app.py              # Streamlit frontend
│
├── data/                   # Folder where uploaded PDFs are stored
│
├── .env                    # Environment variables
├── requirements.txt        # Python dependencies
```

---
## Backend Setup (FastAPI)

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set environment variables in `.env`
```
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENV=your_pinecone_environment
PINECONE_INDEX_NAME=your_index_name
GOOGLE_API_KEY=your_google_api_key
```

### 3. Run FastAPI backend
```bash
uvicorn app.rag.main:app --reload
```
Backend will be available at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---
## PDF Upload & Question API

### Upload a PDF
**Endpoint:** `POST /upload`  
Form-data:  
- `file`: PDF file

### Ask a Question
**Endpoint:** `POST /ask`  
Query:  
- `question`: Your question

---
## Frontend Options

### 1. Streamlit Frontend
**Path:** `streamlit_app/app.py`  
Run with:
```bash
streamlit run streamlit_app/app.py
```
Access at: [http://localhost:8501](http://localhost:8501)

---
### 2. Chainlit Frontend
**Path:** `chainlit_app/rag_chainlit.py`  
Run with:
```bash
chainlit run chainlit_app/rag_chainlit.py
```
Access at: [http://localhost:8000](http://localhost:8000) (Chainlit UI)

---
### 3. Gradio Frontend
**Path:** `gradio_app/app.py`  
Run with:
```bash
python gradio_app/app.py
```
Access at: URL printed in terminal (e.g., `http://127.0.0.1:7860`)

---
## Workflow

1. Start the **FastAPI backend** (`uvicorn app.rag.main:app --reload`).
2. Upload PDFs via `/upload` endpoint or using the frontends.
3. Ask questions using `/ask` endpoint or frontends.
4. RAG service retrieves relevant chunks from Pinecone and answers via Gemini LLM.

---
## Notes
- Make sure Pinecone index exists; it will be created automatically if missing.
- Google Generative AI Embeddings model: `models/embedding-001`
- Chunk size: `1000` chars with `200` overlap.

---
## Requirements
See `requirements.txt` for the full list of dependencies.
