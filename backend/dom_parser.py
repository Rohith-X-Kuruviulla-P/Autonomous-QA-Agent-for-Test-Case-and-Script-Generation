from bs4 import BeautifulSoup

def get_unique_selector(tag) -> str:
    """
    Generates the most robust 'Direct Address' for an element.
    Priority: ID > Name > Placeholder > Button Text > CSS Selector
    """
    # 1. Best Case: ID
    if tag.get('id'):
        return f"By.ID, '{tag.get('id')}'"
    
    # 2. Good Case: Name Attribute (Common in forms)
    if tag.get('name'):
        return f"By.NAME, '{tag.get('name')}'"
    
    # 3. Fallback: Input Placeholder (Very reliable for User Forms)
    if tag.name == 'input' and tag.get('placeholder'):
        return f"By.XPATH, \"//input[@placeholder='{tag.get('placeholder')}']\""
        
    # 4. Fallback: Button Text (Reliable for UI actions)
    if tag.name == 'button':
        text = tag.get_text(strip=True)
        if text:
            return f"By.XPATH, \"//button[normalize-space()='{text}']\""
    
    # 5. Fallback: Link Text
    if tag.name == 'a':
        text = tag.get_text(strip=True)
        if text:
             return f"By.LINK_TEXT, '{text}'"

    return "Selector unavailable (Manual inspection required)"

def parse_html_structure(html_content: str) -> str:
    """
    Scans HTML and returns a 'Selector Map' string for the AI Agent.
    """
    if not html_content: return "No HTML content provided."
    
    soup = BeautifulSoup(html_content, 'html.parser')
    element_map = []
    
    # 1. Map Inputs & Selects
    for inp in soup.find_all(['input', 'textarea', 'select']):
        # Ignore hidden inputs
        if inp.get('type') == 'hidden': continue
        
        label = inp.get('id') or inp.get('name') or inp.get('placeholder') or "Unlabeled Input"
        address = get_unique_selector(inp)
        element_map.append(f"INPUT: '{label}' -> {address}")
        
    # 2. Map Buttons
    for btn in soup.find_all('button'):
        label = btn.get_text(strip=True) or btn.get('id') or "Unlabeled Button"
        address = get_unique_selector(btn)
        element_map.append(f"BUTTON: '{label}' -> {address}")

    # 3. Map Links that look like buttons (Bootstrap btn class)
    for a in soup.find_all('a', class_=True):
        if 'btn' in a.get('class', []):
            label = a.get_text(strip=True)
            if label:
                address = get_unique_selector(a)
                element_map.append(f"LINK/BUTTON: '{label}' -> {address}")

    return "\n".join(element_map)