import streamlit as st
from transformers import pipeline
from utils.logger import get_logger

logger = get_logger(__name__)

# Constants for clarity
DEFAULT_MODEL = "jy46604790/Fake-News-Bert-Detect"
MAX_CHAR_LENGTH = 1500  # Safe truncation for 512 token limit

@st.cache_resource
def load_model():
    """
    Loads and caches the Hugging Face transformer pipeline for fake news text classification.
    """
    try:
        logger.info(f"Loading fake news model: {DEFAULT_MODEL}")
        return pipeline("text-classification", model=DEFAULT_MODEL)
    except Exception as e:
        logger.exception("Failed to load model.")
        raise e

def classify_text(text: str) -> dict:
    """
    Classifies the text as REAL or FAKE using the loaded pipeline.
    Properly handles truncation to avoid token limit errors.
    """
    logger.info("Classification process started.")
    
    if not text or not text.strip():
        logger.warning("Empty text provided for classification.")
        return {"label": "UNKNOWN", "confidence": 0.0, "raw_label": None, "raw_score": 0.0, "model_name": DEFAULT_MODEL}
        
    try:
        model_pipeline = load_model()
        
        # Safely truncate the text
        truncated_text = text[:MAX_CHAR_LENGTH]
        logger.info(f"Truncated text to {len(truncated_text)} characters for inference.")
        
        # Run inference
        result = model_pipeline(truncated_text)[0]
        
        raw_label = result['label']
        raw_score = result['score']
        
        logger.info(f"Model output - raw_label: {raw_label}, raw_score: {raw_score}")
        
        # Map: LABEL_0 -> FAKE, LABEL_1 -> REAL (Common for Fake News models)
        norm_label = raw_label.upper()
        if norm_label in ['LABEL_1', '1', 'RELIABLE', 'TRUE', 'REAL', 'POSITIVE']:
            label = "REAL"
        elif norm_label in ['LABEL_0', '0', 'UNRELIABLE', 'FALSE', 'FAKE', 'NEGATIVE']:
            label = "FAKE"
        else:
            # Fallback
            logger.warning(f"Unexpected label mapping: {raw_label}, defaulting to UNKNOWN")
            label = "UNKNOWN"
            
        logger.info(f"Final mapped label: {label} with confidence {raw_score:.2f}")
        
        return {
            "label": label,
            "confidence": raw_score,
            "raw_label": raw_label,
            "raw_score": raw_score,
            "model_name": DEFAULT_MODEL
        }
        
    except Exception as e:
        logger.exception("Error during text classification.")
        return {"label": "ERROR", "confidence": 0.0, "raw_label": str(e), "raw_score": 0.0, "model_name": DEFAULT_MODEL}
