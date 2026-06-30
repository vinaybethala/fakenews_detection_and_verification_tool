from services.preprocess import clean_text

def test_clean_text_removes_urls():
    text = "Read more at http://example.com"
    assert clean_text(text) == "Read more at"

def test_clean_text_normalizes_whitespace():
    text = "This   is  a\n\ntest."
    assert clean_text(text) == "This is a test."

def test_clean_text_removes_html():
    text = "<p>Hello</p> <b>world</b>"
    assert clean_text(text) == "Hello world"

def test_clean_text_preserves_punctuation():
    text = "Wait, what?! Yes, it's true."
    assert clean_text(text) == "Wait, what?! Yes, it's true."

def test_clean_text_empty_input():
    assert clean_text(None) == ""
    assert clean_text("") == ""
