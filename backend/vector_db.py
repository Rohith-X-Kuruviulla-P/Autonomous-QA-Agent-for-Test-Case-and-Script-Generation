from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from config import settings

def get_vector_db():
    """Returns the ChromaDB instance."""
    embedding_fn = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)
    
    vector_db = Chroma(
        persist_directory=settings.VECTOR_DB_DIR,
        embedding_function=embedding_fn,
        collection_name="project_docs"
    )
    return vector_db

def clear_db():
    """Clears the existing database for a fresh start."""
    db = get_vector_db()
    db.reset_collection()