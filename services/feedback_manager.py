import os
import json
from datetime import datetime

FEEDBACK_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "feedback_data.json")

def _ensure_feedback_file():
    os.makedirs(os.path.dirname(FEEDBACK_FILE), exist_ok=True)
    if not os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)

def load_feedback():
    _ensure_feedback_file()
    try:
        with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def analyze_sentiment(text):
    if not text:
        return "Neutral"
    
    positive_words = {"good", "great", "excellent", "correct", "awesome", "perfect", "accurate", "helpful", "right", "nice", "love", "thanks", "thank you"}
    negative_words = {"bad", "wrong", "terrible", "incorrect", "inaccurate", "useless", "poor", "awful", "hate", "false", "stupid"}

    text_lower = text.lower()
    words = text_lower.replace(",", "").replace(".", "").split()
    
    pos_score = sum(1 for w in words if w in positive_words)
    neg_score = sum(1 for w in words if w in negative_words)

    if pos_score > neg_score:
        return "Positive"
    elif neg_score > pos_score:
        return "Negative"
    else:
        return "Neutral"

def save_feedback(article_text, prediction, actual, feedback_text, rating):
    _ensure_feedback_file()
    
    feedbacks = load_feedback()
    
    sentiment = analyze_sentiment(feedback_text)
    
    new_entry = {
        "text": article_text[:500] + "..." if len(article_text) > 500 else article_text,
        "prediction": prediction,
        "actual": actual,
        "feedback": feedback_text,
        "rating": rating,
        "sentiment": sentiment,
        "timestamp": datetime.now().isoformat()
    }
    
    feedbacks.append(new_entry)
    
    with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
        json.dump(feedbacks, f, indent=4)
        
    return True
