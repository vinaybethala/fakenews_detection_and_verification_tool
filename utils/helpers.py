def format_confidence(confidence: float) -> str:
    """Formats confidence score as a percentage string."""
    try:
        return f"{float(confidence) * 100:.2f}%"
    except (TypeError, ValueError):
        return "0.00%"

def truncate_text(text: str, max_length: int = 512) -> str:
    """Truncates text safely to a maximum length."""
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length].rsplit(' ', 1)[0] + '...'
