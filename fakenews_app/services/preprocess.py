import re
from utils.logger import get_logger

logger = get_logger(__name__)

def clean_text(text: str) -> str:
    """
    Cleans and preprocesses the text for NLP tasks.
    Removes noisy symbols, normalizes whitespace, and strips extra spaces.
    Keeps punctuation and numeric symbols (%, $) intact for accurate claim extraction.
    """
    if not text:
        logger.warning("Empty text passed to clean_text.")
        return ""

    logger.info(f"Preprocessing text of length {len(text)}")

    # Remove HTML tags if any
    text = re.sub(r'<[^>]*>', ' ', text)

    # Remove URLs
    text = re.sub(r'https?://\S+', ' ', text)

    # Normalize whitespace: replace tabs, newlines, multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)

    # Remove special noisy characters but KEEP:
    #   - word chars (\w), spaces (\s)
    #   - basic punctuation: . , ! ? ' " - —
    #   - numeric symbols: % $
    text = re.sub(r"[^\w\s\.,!?'\"\-\%\$]", '', text)

    cleaned = text.strip()
    logger.info(f"Preprocessing completed. Final length: {len(cleaned)}")

    return cleaned
