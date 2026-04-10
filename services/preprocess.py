import re

def clean_text(text: str) -> str:
    """
    Remove URLs, special chars (!@#$ etc except . , ?), normalize whitespace, lowercase.
    """
    if not isinstance(text, str):
        return ""
    
    text = text.lower()
    
    # Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    
    # Remove HTML tags just in case
    text = re.sub(r'<.*?>', '', text)
    
    # Keep alphanumeric and punctuation: . , ?
    text = re.sub(r'[^a-z0-9\s.,?]', '', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text
