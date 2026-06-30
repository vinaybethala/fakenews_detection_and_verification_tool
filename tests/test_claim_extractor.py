from services.claim_extractor import extract_claims

def test_extract_claims_finds_reporting_verb():
    text = "The quick brown fox jumps. The government announced a new policy today."
    claims = extract_claims(text)
    assert "The government announced a new policy today." in claims

def test_extract_claims_finds_numbers():
    text = "This is meaningless. Sales increased by 50% this year."
    claims = extract_claims(text)
    assert "Sales increased by 50% this year." in claims

def test_extract_claims_limits_to_three():
    text = "The study shows 1. The agency said 2. Officials confirmed 3. Data revealed 4."
    claims = extract_claims(text)
    assert len(claims) <= 3

def test_extract_claims_removes_duplicates():
    text = "The agency reported 50% growth. The agency reported 50% growth. Another normal sentence."
    claims = extract_claims(text)
    assert claims.count("The agency reported 50% growth.") == 1

def test_extract_claims_fallback_first_meaningful():
    text = "Short. This is a perfectly normal sentence with no special words but long enough to be kept. Another one."
    claims = extract_claims(text)
    assert len(claims) == 1
    assert "This is a perfectly normal sentence with no special words but long enough to be kept." in claims[0]

def test_extract_claims_empty_input():
    assert extract_claims(None) == []
    assert extract_claims("") == []
