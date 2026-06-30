from services.explain import explain_prediction

def test_explain_fake_with_suspicious():
    text = "This is a shocking secret miracle!"
    pred = {"label": "FAKE", "confidence": 0.9}
    reasons = explain_prediction(text, pred, [])
    assert any("miracle" in r.lower() or "shocking" in r.lower() for r in reasons)
    assert any("FAKE" in r or "unreliable content" in r for r in reasons)

def test_explain_real_with_credible():
    text = "According to official data reported by researchers."
    pred = {"label": "REAL", "confidence": 0.85}
    reasons = explain_prediction(text, pred, ["Claim 1"])
    assert any("official data" in r.lower() or "reported by" in r.lower() for r in reasons)
    assert any("1 factual assertions" in r.lower() for r in reasons)

def test_explain_low_confidence():
    text = "A normal text without much."
    pred = {"label": "REAL", "confidence": 0.55}
    reasons = explain_prediction(text, pred, [])
    assert any("confidence is relatively low" in r.lower() for r in reasons)
