from utils.logger import get_logger

logger = get_logger(__name__)

def explain_prediction(text: str, prediction_data: dict, extracted_claims: list[str]) -> list[str]:
    """
    Generates human-readable explanations based on language indicators.
    """
    if not text:
        return ["No text provided to explain."]
        
    logger.info("Generating explanation for prediction.")
    reasons = []
    text_lower = text.lower()
    
    suspicious_words = ["miracle", "shocking", "secret", "100%", "guarantee", "click here", "you won't believe"]
    credibility_indicators = ["according to", "reported by", "official data", "study shows", "government", "researchers"]
    
    found_suspicious = [word for word in suspicious_words if word in text_lower]
    found_credible = [phrase for phrase in credibility_indicators if phrase in text_lower]
    
    label = prediction_data.get("label")
    confidence = prediction_data.get("confidence", 0.0)
    
    if label == "FAKE":
        reasons.append(f"The model detected language patterns commonly associated with potentially unreliable content (Confidence: {confidence*100:.1f}%).")
        if found_suspicious:
            reasons.append(f"Suspicious or clickbait terminology was detected: {', '.join(found_suspicious)}.")
        if not found_credible:
            reasons.append("The text lacks authoritative references like 'reported by' or 'official data'.")
    elif label == "REAL":
        reasons.append(f"The text structure aligns with standard news reporting or objective statements (Confidence: {confidence*100:.1f}%).")
        if found_credible:
            reasons.append(f"Credibility indicators found: {', '.join(found_credible)}.")
        if not found_suspicious:
            reasons.append("No common clickbait keywords were detected.")
            
    if extracted_claims:
        reasons.append(f"Successfully extracted {len(extracted_claims)} factual assertions for independent verification.")
        
    if confidence < 0.6:
        reasons.append("Note: The model's confidence is relatively low, meaning the stylistic indicators are mixed.")
        
    if not reasons:
        reasons.append("The text contains standard language with no strong positive or negative stylistic signals.")
        
    logger.info(f"Generated {len(reasons)} explanation points.")
    return reasons
