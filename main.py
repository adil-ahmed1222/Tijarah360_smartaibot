from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# Import chatbot and Supabase-backed RAG logic
from chatbot import get_chatbot_response
from langchain_chain import get_rag_response, create_and_store_embedding, get_documents_count, debug_vector_search

# Initialize FastAPI app
app = FastAPI()

# Enable CORS for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Log Supabase document count on startup
@app.on_event("startup")
def startup_event():
    count = get_documents_count()
    print(f"✅ Supabase has {count} documents in the vector table.")

# Request models
class ChatRequest(BaseModel):
    query: str

class EmbeddingRequest(BaseModel):
    text: str
    metadata: dict = {}

# Health check route
@app.get("/")
def read_root():
    return {"message": "Tijarah360 AI Assistant is ready!"}


# Count documents in Supabase vector table
@app.get("/count")
def count_endpoint():
    count = get_documents_count()
    return {"count": count}

# Simple chatbot (LLM-only)
@app.post("/chat")
def chat_endpoint(req: ChatRequest):
    reply = get_chatbot_response(req.query)
    return {"response": reply}

# RAG-based chatbot using Supabase
@app.post("/rag_chat")
def rag_chat_endpoint(req: ChatRequest):
    user_query = req.query.strip().lower()

    # Special case: ask about document count
    if user_query in [
        "how many articles are loaded",
        "how many documents in the database",
        "how many entries are in the knowledge base",
        "how many issues are loaded"
    ]:
        count = get_documents_count()
        return {"response": f"There are currently {count} articles loaded into the system."}

    # Default response from Supabase vector search
    reply = get_rag_response(req.query)
    return {"response": reply}

# Add a new document to Supabase vector store
@app.post("/create-embedding")
def create_embedding_endpoint(req: EmbeddingRequest):
    result = create_and_store_embedding(req.text, req.metadata)
    return {"embedding_result": result}

# Debug endpoint to test vector similarity search
@app.post("/debug-search")
def debug_search_endpoint(req: ChatRequest):
    """Debug endpoint to see what's happening with vector similarity search"""
    results = debug_vector_search(req.query, k=5)
    return {
        "query": req.query,
        "results": results,
        "total_results": len(results)
    }
