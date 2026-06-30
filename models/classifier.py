import streamlit as st
import random
from utils.logger import get_logger

logger = get_logger(__name__)

DEFAULT_MODEL = "Heuristic-Rule-Based"

def classify_text(text: str) -> dict:
    """
    Classifies the text as REAL or FAKE using a heuristic approach.
    Fast and requires no model downloads.
    """
    logger.info("Classification process started (Heuristic Mode).")
    
    if not text or not text.strip():
        logger.warning("Empty text provided for classification.")
        return {"label": "UNKNOWN", "confidence": 0.0, "raw_label": None, "raw_score": 0.0, "model_name": DEFAULT_MODEL}
        
    try:
        text_lower = text.lower()
        suspicious_words = [
            "miracle", "shocking", "secret", "100%", "guarantee", 
            "click here", "you won't believe", "suppressed", "government hiding",
            "conspiracy", "hidden agenda", "scientists shocked", "breakthrough cure"
        ]
        
        found_suspicious = sum(1 for word in suspicious_words if word in text_lower)
        
        # Calculate a pseudo-confidence score based on suspicious keywords
        if found_suspicious > 0:
            label = "FAKE"
            # More suspicious words = higher confidence, capped at 0.98
            confidence = min(0.65 + (found_suspicious * 0.1), 0.98)
        else:
            label = "REAL"
            # Based on length for pseudo-realism, capped at 0.95
            confidence = min(0.70 + (len(text) / 10000.0), 0.95)
            
        logger.info(f"Final mapped label: {label} with confidence {confidence:.2f}")
        
        return {
            "label": label,
            "confidence": confidence,
            "raw_label": label,
            "raw_score": confidence,
            "model_name": DEFAULT_MODEL
        }
        
    except Exception as e:
        logger.exception("Error during text classification.")
        return {"label": "ERROR", "confidence": 0.0, "raw_label": str(e), "raw_score": 0.0, "model_name": DEFAULT_MODEL}
