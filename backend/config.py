import os

class Settings:
    # Paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    UPLOAD_DIR = os.path.join(BASE_DIR, "assets", "uploads")
    VECTOR_DB_DIR = os.path.join(BASE_DIR, "data", "chroma_db")
    
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2" # Runs locally

    GEMINI_API_KEY = "AIzaSyA9FmcmmAy39ZFfEQuwsmWakp_YMvdE5KA"  
    GEMINI_MODEL = "gemini-2.5-flash"  

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(VECTOR_DB_DIR, exist_ok=True)

settings = Settings()