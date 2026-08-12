import os
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from rag_engine import load_and_split_document, create_vector_store, query_rag_system

load_dotenv()

app = FastAPI(
    title="Document Q&A RAG Backend API",
    description="FastAPI Backend for PDF Q&A using LangChain, FAISS, and Groq LLMs",
    version="1.0.0"
)

# Enable CORS for decoupled frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global in-memory storage for vector store instance
app_state = {
    "vector_store": None,
    "doc_name": None
}

class QueryRequest(BaseModel):
    question: str
    groq_api_key: Optional[str] = None
    model_name: Optional[str] = "llama-3.3-70b-versatile"

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "indexed_doc": app_state["doc_name"]}

@app.post("/api/upload")
async def upload_document(
    file: UploadFile = File(...),
    chunk_size: int = Form(1000),
    chunk_overlap: int = Form(200)
):
    try:
        contents = await file.read()
        file_name = file.filename
        
        chunks = load_and_split_document(contents, file_name, chunk_size, chunk_overlap)
        vector_store = create_vector_store(chunks)
        
        app_state["vector_store"] = vector_store
        app_state["doc_name"] = file_name
        
        return {
            "message": f"Successfully indexed '{file_name}'",
            "filename": file_name,
            "total_chunks": len(chunks)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process document: {str(e)}"
        )

@app.post("/api/query")
def ask_question(payload: QueryRequest):
    if app_state["vector_store"] is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No document has been uploaded/indexed yet. Please upload a document first."
        )

    # Determine Groq API key (payload or env)
    api_key = payload.groq_api_key or os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Groq API Key is required. Provide it in request body or backend .env file."
        )

    try:
        result = query_rag_system(
            vector_store=app_state["vector_store"],
            question=payload.question,
            groq_api_key=api_key,
            model_name=payload.model_name
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query failed: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
