import re
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser
from vector_db import get_vector_db
from config import settings
from dom_parser import parse_html_structure

# --- 1. Robust Data Models (Crash-Proof) ---
class TestCase(BaseModel):
    test_id: str = Field(description="Unique test case ID (e.g., TC-001)")
    # Defaults added to prevent crashes if LLM output is imperfect
    feature: str = Field(default="General Feature", description="Feature being tested")
    test_type: str = Field(default="Functional", description="Type: positive, negative, boundary, or edge case")
    scenario: str = Field(default="No description provided", description="Detailed test scenario description")
    preconditions: str = Field(default="None", description="Prerequisites before test execution")
    test_steps: List[str] = Field(default_factory=list, description="Step-by-step test execution instructions")
    expected_result: str = Field(default="No specific result", description="Expected outcome")
    grounded_in: str = Field(default="Unknown Source", description="Source document filename(s)")
    priority: str = Field(default="Medium", description="Priority: High, Medium, Low")

class TestPlan(BaseModel):
    test_cases: List[TestCase] = Field(description="List of generated test cases")

# --- 2. Helper Functions ---
def _clean_code_output(code: str) -> str:
    """Remove markdown formatting (```python) from code output."""
    code = re.sub(r'^```python\s*\n', '', code, flags=re.MULTILINE)
    code = re.sub(r'^```\s*\n', '', code, flags=re.MULTILINE)
    code = re.sub(r'\n```\s*$', '', code)
    return code.strip()

# --- 3. Agent 1: The Test Strategist ---
def generate_test_cases_agent(query: str) -> Dict:
    """
    Generates structured test cases using RAG + JSON Mode.
    """
    # A. Retrieval
    db = get_vector_db()
    retriever = db.as_retriever(search_kwargs={"k": 6})
    docs = retriever.invoke(query)
    
    # Format context with source citation
    context_parts = []
    for doc in docs:
        source = doc.metadata.get('source', 'Unknown')
        context_parts.append(f"[Source: {source}]\n{doc.page_content}")
    context_str = "\n\n".join(context_parts)

    # B. Setup LLM
    llm = ChatOllama(
        model=settings.LLM_MODEL,
        temperature=0.1, 
        num_predict=4096,
        format="json" # Strict JSON enforcement
    )
    parser = PydanticOutputParser(pydantic_object=TestPlan)

    # C. Prompt (The "Original" Detailed Version)
    system_prompt = """You are an Expert QA Test Lead.
    
    INSTRUCTIONS:
    1. Analyze the provided documentation context.
    2. Generate a comprehensive test plan based ONLY on that context.
    3. Output must be a valid JSON object matching the schema below.
    4. Do NOT include any conversational text, preambles, or markdown formatting. Just the JSON.
    5. 'grounded_in' must cite the source filename from the context.

    DOCUMENTATION CONTEXT:
    {context}

    JSON SCHEMA:
    {format_instructions}
    """

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "Generate test plan for: {query}")
    ])

    chain = prompt | llm | parser

    try:
        result = chain.invoke({
            "context": context_str,
            "query": query,
            "format_instructions": parser.get_format_instructions()
        })
        return result.dict()
    except Exception as e:
        # Return error dict for UI handling
        return {"error": f"Agent Generation Failed: {str(e)}"}

# --- 4. Agent 2: The Selenium Engineer (Hybrid Approach) ---
def generate_selenium_script_agent(test_case_json: str, html_content: str) -> str:
    """
    Generates a Selenium script using the 'Direct Address' map from dom_parser.
    """
    # A. Get Direct Addresses (The Truth Source)
    # This uses the separate dom_parser.py file to analyze the HTML
    valid_selectors = parse_html_structure(html_content)

    # B. Setup LLM
    llm = ChatOllama(
        model=settings.LLM_MODEL,
        temperature=0.2, # Slightly higher for code creativity
        num_predict=6000
    )

    # C. Prompt (The "Original" Detailed Version)
    system_prompt = """You are a Senior QA Automation Engineer (Python + Selenium).
    
    CRITICAL INSTRUCTION:
    You are provided with a 'Selector Map' below containing the valid elements found in the HTML.
    You MUST use the exact selectors provided in this map. Do NOT guess IDs.
    
    SELECTOR MAP (Use these addresses):
    {selectors}

    INSTRUCTIONS:
    1. Act as a Selenium automation expert.
    2. Write a complete, runnable Python Selenium version 4+ script for the provided Test Case.
    3. Use appropriate selectors (IDs, names, CSS selectors) based on the Selector Map.
    4. Produce high-quality, fully executable code.
    5. 
    
    STRICT CODE REQUIREMENTS (DO NOT VIOLATE):
    1. **Selenium 4 Syntax Only**: 
       - USE: `driver.find_element(By.ID, 'id')`
       - DO NOT USE: `find_element_by_id` (Deprecated)
    
    2. **Explicit Waits (WebDriverWait)**:
       - USE: `WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'id')))`
       - NOTE: You must pass a TUPLE `((By..., ...))` to the EC condition. Double parentheses are required!
    
    3. **Python Naming Conventions**:
       - USE: `element_to_be_clickable` (Snake Case)
       - DO NOT USE: `elementToBeClickable` (Camel Case/Java style)

    4. **Robustness**:
       - Include `try/except` blocks to catch errors.
       - Print "TEST PASSED" or "TEST FAILED" explicitly.
       - Include `teardown()` to close the driver.

    5. **Self-Contained**:
       - Include ALL imports: `webdriver`, `By`, `WebDriverWait`, `EC`, `TimeoutException`.
       - Do not assume any external setup.

    OUTPUT FORMAT:
    - Return ONLY the raw Python code.
    - No markdown formatting (no ```python blocks).
    - No explanations text.
    """

    # Only send test case logic in the user prompt to save context
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "Here is the Test Case to automate:\n{test_case}")
    ])

    chain = prompt | llm | StrOutputParser()

    try:
        result = chain.invoke({
            "selectors": valid_selectors,
            "test_case": test_case_json
        })
        return _clean_code_output(result)
    except Exception as e:
        return f"# Error generating script: {str(e)}"