import os
os.environ.pop("SSL_CERT_FILE", None)
import shutil
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from typing import List
from config import settings
from ingestion import ingest_documents
from vector_db import clear_db
from agents import generate_test_cases_agent, generate_selenium_script_agent, TestPlan

app = FastAPI(title="Sentinel-QA")

#rest of your code remains the same
@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """
    Clears DB and ingests new files (HTML + Docs).
    """
    clear_db() # Reset for the new project assignment
    saved_paths = []
    
    for file in files:
        file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        saved_paths.append(file_path)
        
    # Trigger Ingestion
    try:
        num_chunks = ingest_documents(saved_paths)
        return {"message": "Knowledge Base Built", "chunks": num_chunks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-tests", response_model=TestPlan)
async def generate_tests(query: str = Form(...)):
    """
    Generates test cases based on the user query.
    """
    result = generate_test_cases_agent(query)
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result

@app.post("/generate-script")
async def generate_script(test_case: str = Form(...), html_filename: str = Form(...)):
    """
    Generates a Selenium script for a specific test case.
    """
    #Load the raw HTML to feed to the Agent
    html_path = os.path.join(settings.UPLOAD_DIR, html_filename)
    if not os.path.exists(html_path):
        raise HTTPException(status_code=404, detail="HTML file not found.")
        
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
        
    script = generate_selenium_script_agent(test_case, html_content)
    return {"script": script}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)