import os
from dotenv import load_dotenv

class Settings:
    load_dotenv()
    # Paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    UPLOAD_DIR = os.path.join(BASE_DIR, "assets", "uploads")
    VECTOR_DB_DIR = os.path.join(BASE_DIR, "data", "chroma_db")
    
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2" 

    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY2")
    GEMINI_MODEL = "gemini-2.5-flash"  

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(VECTOR_DB_DIR, exist_ok=True)

settings = Settings()