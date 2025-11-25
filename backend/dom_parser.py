# dom_parser.py
from bs4 import BeautifulSoup

def get_clean_html_tree(html_content: str) -> str:
    """Enhanced parser that provides better context for element discovery"""
    if not html_content: 
        return "No HTML content provided"

    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove non-interactive elements
    for element in soup(["script", "style", "svg", "link", "meta", "noscript"]):
        element.decompose()

    # Keep all interactive and structural elements
    interactive_tags = [
        'input', 'button', 'select', 'textarea', 'form', 'a', 'label',
        'div', 'span', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'ul', 'ol', 'li', 'table', 'tr', 'td', 'th', 'section', 'article'
    ]

    cleaned_elements = []
    
    for element in soup.find_all(interactive_tags):
        element_info = f"<{element.name}"
        
        # Add all relevant attributes for Selenium
        attributes = ['id', 'name', 'type', 'placeholder', 'value', 'class', 'for', 'href', 'role', 'aria-label']
        for attr in attributes:
            attr_value = element.get(attr)
            if attr_value:
                # Truncate long values
                if len(str(attr_value)) > 50:
                    attr_value = str(attr_value)[:47] + "..."
                element_info += f' {attr}="{attr_value}"'
        
        element_info += ">"
        
        # Add meaningful text content (limited length)
        text_content = element.get_text(strip=True)
        if text_content and len(text_content) < 100:
            # Clean up whitespace for better readability
            text_content = ' '.join(text_content.split())
            element_info += f" {text_content}"
            
        element_info += f"</{element.name}>"
        cleaned_elements.append(element_info)

    return "\n".join(cleaned_elements) if cleaned_elements else "No interactive elements found"