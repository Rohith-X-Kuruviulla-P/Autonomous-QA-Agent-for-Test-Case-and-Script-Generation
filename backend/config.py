import os

class Settings:
    # Paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    UPLOAD_DIR = os.path.join(BASE_DIR, "assets", "uploads")
    VECTOR_DB_DIR = os.path.join(BASE_DIR, "data", "chroma_db")
    
    # LLM Settings 
    LLM_MODEL = "llama3"  # Ensure you have this pulled in Ollama
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2" # Runs locally

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(VECTOR_DB_DIR, exist_ok=True)

settings = Settings()