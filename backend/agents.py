
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

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)

# --- 1. Data Models ---
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

# --- 2. Helpers ---
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

# --- 3. Agent 1: The Test Strategist ---
def generate_test_cases_agent(query: str) -> Dict:
    """Generates structured test cases using RAG + JSON Mode."""
    db = get_vector_db()
    retriever = db.as_retriever(search_kwargs={"k": 6})
    docs = retriever.invoke(query)
    
    context_str = "\n\n".join([f"[Source: {d.metadata.get('source', 'Unknown')}]\n{d.page_content}" for d in docs])

    # Keep the same prompt structure
    system_prompt = """You are an Expert QA Test Lead.
    INSTRUCTIONS:
    1. Analyze the provided context.
    2. Generate a test plan based ONLY on that context.
    3. Output must be valid JSON matching the EXAMPLE below.
    4. Do NOT output schema definitions (defs/properties)."""

    user_prompt = f"""
CONTEXT:
{context_str}

JSON EXAMPLE:
{{
    "test_cases": [
        {{
            "test_id": "TC-001",
            "feature": "Login",
            "test_type": "Positive",
            "scenario": "Successful login",
            "preconditions": "User is on login page",
            "test_steps": ["Enter user", "Click Login"],
            "expected_result": "Dashboard loads",
            "grounded_in": "auth.md",
            "priority": "High"
        }}
    ]
}}

Generate test plan for: {query}
"""

    try:
        # Replace LangChain call with Gemini
        response_text = _call_gemini(user_prompt, system_prompt)
        
        # Parse JSON response manually since we're not using PydanticOutputParser
        response_text = response_text.strip()
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
            
        result_dict = json.loads(response_text)
        return result_dict
    except Exception as e:
        return {"error": f"Agent Generation Failed: {str(e)}"}

# --- 4. Agent 2: The Selenium Engineer (YOUR OPTIMIZED VERSION) ---
def generate_selenium_script_agent(test_case_json: str, html_content: str) -> str:
    """
    Generates robust Selenium scripts that test REAL user behavior, not just typing.
    """
    clean_html = get_clean_html_tree(html_content)

    system_prompt = """You are a Senior QA Automation Engineer specializing in robust, production-grade Selenium 4 (Python)."""
    user_prompt = f"""

═══════════════════════════════════════════════════════════════════════════
INPUT CONTEXT
═══════════════════════════════════════════════════════════════════════════
1. HTML SKELETON: A simplified view of the actual DOM. This is your ONLY source of truth.
{clean_html}

2. TEST CASE: The user flow you must automate.

═══════════════════════════════════════════════════════════════════════════
CRITICAL RULES: SELECTORS (ZERO TOLERANCE FOR HALLUCINATIONS)
═══════════════════════════════════════════════════════════════════════════
1. **Strict Existence Check:** You MUST NOT invent IDs, Names, or Classes. If an attribute is not visible in the HTML SKELETON above, it does not exist.
2. **Attribute Confusion:** Do not confuse `name="q"` with `id="q"`. Use the specific locator (`By.NAME` vs `By.ID`) that matches the skeleton.
3. **Text Matching (XPath):** - NEVER use `text()='...'` on container tags (`div`, `span`, `form`). It fails if the element has child tags.
   - ALWAYS use `contains(., 'Text')` to match text inside an element tree.
   - *Correct:* `//button[contains(., 'Add to Cart')]`
4. **Radio/Checkbox Logic:**
   - Do NOT select by the visible text label (e.g., "Credit Card").
   - Look at the `<input>` in the skeleton. Use its `value` attribute or specific `id`.
   - *Correct:* `//input[@name='payment' and @value='cc']`

═══════════════════════════════════════════════════════════════════════════
CRITICAL RULES: INTERACTION LOGIC
═══════════════════════════════════════════════════════════════════════════
1. **Dropdowns (<select>):** - You MUST use the `Select` class.
   - `Select(driver.find_element(...)).select_by_visible_text("Option Name")`.
   - NEVER use `.send_keys()` or `.click()` on options directly.
2. **Wait Strategy:** - NEVER use `time.sleep()` for synchronization.
   - USE `WebDriverWait(driver, 10).until(...)` for EVERY interaction.
   - `EC.element_to_be_clickable` -> For Buttons, Links, Inputs.
   - `EC.visibility_of_element_located` -> For Success Messages/Headings.
   - `EC.presence_of_element_located` -> Only for hidden DOM elements.
3. **Prerequisites:** - If the test assumes a state (e.g., "Checkout"), you must perform the setup steps (e.g., "Add item to cart") first, even if not explicitly stated in the simple test case description.

═══════════════════════════════════════════════════════════════════════════
CODE STRUCTURE & QUALITY
═══════════════════════════════════════════════════════════════════════════
1. **Imports:** Include all: `webdriver`, `By`, `WebDriverWait`, `EC`, `Select`, `TimeoutException`, `NoSuchElementException`.
2. **Setup:** - Use `options = webdriver.ChromeOptions()`.
   - Use `options.add_argument('--headless')` (unless debugging).
   - Use `driver = webdriver.Chrome(options=options)`.
3. **Error Handling:**
   - Wrap the logic in `try...except...finally`.
   - Catch `TimeoutException` and print a clear "FAILED: Element not found" message.
   - Ensure `driver.quit()` is in the `finally` block.
4. **Verification (Assertions):**
   - Verify success by checking for **VISIBLE UI Elements** (Text, Success Messages, Page Headers).
   - Do NOT verify by checking HTTP status codes or hidden backend IDs unless explicitly shown in the skeleton.
   - Print "SUCCESSFUL" only if assertions pass.
5. **File URL**: use `driver.get("file:///path/to/uploaded/file.html")` to load the HTML file.
═══════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT
═══════════════════════════════════════════════════════════════════════════
- Return ONLY the raw Python code string.
- NO Markdown blocks (```python).
- NO conversational filler ("Here is your script").

"""

    try:
        # Replace LangChain call with Gemini
        result = _call_gemini(user_prompt, system_prompt)
        return _clean_code_output(result)
    except Exception as e:
        return f"# Error generating script: {str(e)}"
    
    