from utils.helpers import format_confidence, truncate_text

def test_format_confidence():
    assert format_confidence(0.854) == "85.40%"
    assert format_confidence(1.0) == "100.00%"
    assert format_confidence(0.0) == "0.00%"

def test_truncate_text():
    text = "Hello world! This is a long string that we want to truncate."
    truncated = truncate_text(text, max_length=15)
    assert len(truncated) <= 18 # up to 15 + "..."
    assert truncated.endswith("...")
    
def test_truncate_text_short():
    assert truncate_text("Short", max_length=50) == "Short"

def test_truncate_text_empty():
    assert truncate_text("", 50) == ""
    assert truncate_text(None, 50) == ""
