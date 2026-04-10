import spacy
import os

# Load global spacy model safely
nlp = None

def load_spacy():
    global nlp
    if nlp is None:
        try:
            nlp = spacy.load("en_core_web_sm")
        except Exception:
            try:
                # Fallback to download and load
                import spacy.cli
                spacy.cli.download("en_core_web_sm")
                nlp = spacy.load("en_core_web_sm")
            except Exception as e:
                print(f"Failed to load spacy: {e}")
                nlp = None

load_spacy()

def extract_claims(text: str) -> list[str]:
    """
    Extract claims: Sentence splitter, filter len>=6 words, no questions (ends ?), dedupe.
    """
    if nlp is None or not text:
        # Fallback simplistic extraction
        sentences = [s.strip() for s in text.replace('!', '.').split('.') if s.strip()]
    else:
        doc = nlp(text)
        sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
    
    claims = []
    seen = set()
    
    for sentence in sentences:
        # Filter logic
        words = sentence.split()
        if len(words) < 6:
            continue
            
        if sentence.endswith('?'):
            continue
            
        # Dedupe
        lower_sent = sentence.lower()
        if lower_sent not in seen:
            seen.add(lower_sent)
            claims.append(sentence)
            
    return claims
