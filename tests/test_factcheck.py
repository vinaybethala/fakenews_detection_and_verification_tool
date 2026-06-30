from unittest.mock import patch, Mock
import requests
from services.factcheck import check_claim, fact_check_claims

@patch('services.factcheck.get_api_key')
def test_check_claim_missing_api_key(mock_get_api_key):
    mock_get_api_key.return_value = None
    result = check_claim("test")
    assert result == {"error": "API Key not found"}

@patch('services.factcheck.requests.get')
@patch('services.factcheck.get_api_key')
def test_check_claim_success(mock_get_api_key, mock_get):
    mock_get_api_key.return_value = "fake_key"
    mock_response = Mock()
    mock_response.json.return_value = {
        "claims": [{
            "claimReview": [{
                "publisher": {"name": "Test Publisher"},
                "textualRating": "False",
                "url": "http://test.com"
            }]
        }]
    }
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    result = check_claim("The earth is flat")
    assert result is not None
    assert result["verdict"] == "False"
    assert result["publisher"] == "Test Publisher"

@patch('services.factcheck.requests.get')
@patch('services.factcheck.get_api_key')
def test_check_claim_empty_response(mock_get_api_key, mock_get):
    mock_get_api_key.return_value = "fake_key"
    mock_response = Mock()
    mock_response.json.return_value = {}
    mock_get.return_value = mock_response

    assert check_claim("Unknown fact") is None

@patch('services.factcheck.check_claim')
def test_fact_check_claims(mock_check_claim):
    mock_check_claim.side_effect = [
        {"claim": "Claim 1", "verdict": "False", "publisher": "Pub", "link": "link1"},
        None
    ]
    results = fact_check_claims(["Claim 1", "Claim 2"])
    assert len(results) == 2
    assert results[0]["verdict"] == "False"
    assert results[1]["verdict"] == "No verified fact-check found"
