from services.source_checker import check_source_trust

def test_check_source_trust_exact_match():
    assert check_source_trust("BBC") == "Trusted"
    assert check_source_trust("Reuters") == "Trusted"

def test_check_source_trust_case_insensitive():
    assert check_source_trust("bbc") == "Trusted"
    assert check_source_trust("THE HINDU") == "Trusted"

def test_check_source_trust_partial_match():
    assert check_source_trust("BBC News") == "Trusted"
    assert check_source_trust("Al Jazeera English") == "Trusted"

def test_check_source_trust_unverified():
    assert check_source_trust("Random Blog") == "Unverified"
    
def test_check_source_trust_surrounding_spaces():
    assert check_source_trust("  CNN  ") == "Trusted"

def test_check_source_trust_empty():
    assert check_source_trust("") == "Unverified"
    assert check_source_trust("   ") == "Unverified"
    assert check_source_trust(None) == "Unverified"
