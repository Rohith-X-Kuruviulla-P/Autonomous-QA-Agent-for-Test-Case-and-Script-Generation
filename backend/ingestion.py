import os
from langchain_community.document_loaders import TextLoader, BSHTMLLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from vector_db import get_vector_db

def ingest_documents(file_paths: list[str]):
    docs = []
    for path in file_paths:
        ext = path.split(".")[-1].lower()
        
        try:
            # Use BSHTMLLoader for HTML
            if ext == "html":
                loader = BSHTMLLoader(path)
            # Use simple TextLoader for MD, TXT, and everything else
            else:
                loader = TextLoader(path, encoding="utf-8")
            
            loaded_docs = loader.load()
            
            # Tag source for traceability
            for doc in loaded_docs:
                doc.metadata["source"] = os.path.basename(path)
            docs.extend(loaded_docs)
            
        except Exception as e:
            print(f"Error loading {path}: {e}")
            continue

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)

    if splits:
        vector_db = get_vector_db()
        vector_db.add_documents(splits)
        
    return len(splits)