import os
import re
import json
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
import google.generativeai as genai
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser
from vector_db import get_vector_db
from config import settings
from dom_parser import get_clean_html_tree
from prompts.prompt_manager import prompt_manager

# Configure Gemini
genai.configure(api_key=settings.GOOGLE_API_KEY)

# Data Models
class TestCase(BaseModel):
    test_id: str = Field(description="Unique test case ID (e.g., TC-001)")
    feature: str = Field(default="General", description="Feature being tested")
    test_type: str = Field(default="Positive", description="Type: positive, negative, boundary")
    scenario: str = Field(default="No description", description="Test scenario")
    preconditions: str = Field(default="None", description="Prerequisites")
    test_steps: List[str] = Field(default_factory=list, description="Step-by-step instructions")
    expected_result: str = Field(default="Success", description="Expected result")
    grounded_in: str = Field(default="Unknown", description="Source doc")
    priority: str = Field(default="Medium", description="Priority")

class TestPlan(BaseModel):
    test_cases: List[TestCase]

#  Helpers
def _clean_code_output(code: str) -> str:
    """Remove markdown formatting (```python) from code output."""
    code = re.sub(r'^```python\s*\n', '', code, flags=re.MULTILINE)
    code = re.sub(r'^```\s*\n', '', code, flags=re.MULTILINE)
    code = re.sub(r'\n```\s*$', '', code)
    return code.strip()

def _call_gemini(prompt: str, system_instruction: str = "") -> str:
    """Helper to call Gemini API maintaining same interface as LangChain"""
    try:
        model = genai.GenerativeModel(
            model_name=settings.GEMINI_MODEL,
            system_instruction=system_instruction
        )
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        raise Exception(f"Gemini API error: {str(e)}")

# Agent 1: The Test Strategist 
def generate_test_cases_agent(query: str) -> Dict:
    """Generates structured test cases using RAG + JSON Mode."""
    db = get_vector_db()
    retriever = db.as_retriever(search_kwargs={"k": 6})
    docs = retriever.invoke(query)
    
    context_str = "\n\n".join([f"[Source: {d.metadata.get('source', 'Unknown')}]\n{d.page_content}" for d in docs])

   
    prompts = prompt_manager.get_combined_prompt(
        "test_strategist",
        context_str=context_str,
        query=query
    )

    try:
        response_text = _call_gemini(prompts['user'], prompts['system'])
        
        response_text = response_text.strip()
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
            
        result_dict = json.loads(response_text)
        return result_dict
    except Exception as e:
        return {"error": f"Agent Generation Failed: {str(e)}"}




# Agent 2: The Selenium Engineer
def generate_selenium_script_agent(test_case_json: str, html_content: str) -> str:
    """Generates robust Selenium scripts that test REAL user behavior."""
    clean_html = get_clean_html_tree(html_content)

    # Get prompts from YAML
    prompts = prompt_manager.get_combined_prompt(
        "selenium_engineer",
        clean_html=clean_html,
        test_case_json=test_case_json
    )

    try:
        result = _call_gemini(prompts['user'], prompts['system'])
        return _clean_code_output(result)
    except Exception as e:
        return f"# Error generating script: {str(e)}"