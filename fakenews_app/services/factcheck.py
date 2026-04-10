import os
import requests
import streamlit as st
from utils.logger import get_logger

logger = get_logger(__name__)

def get_api_key():
    """Retrieves the Google Fact Check API key."""
    # Priority 1: Session state (dynamic configuration)
    if st.session_state.get("admin_api_key"):
        return st.session_state["admin_api_key"]
        
    # Priority 2: Environment variables
    key = os.getenv("GOOGLE_FACTCHECK_API_KEY")
    if key:
        return key
    
    # Priority 3: Streamlit secrets
    try:
        if "GOOGLE_FACTCHECK_API_KEY" in st.secrets:
            return st.secrets["GOOGLE_FACTCHECK_API_KEY"]
    except Exception:
        pass
        
    return None

def check_claim(claim: str) -> dict:
    """
    Queries the Google Fact Check API for a specific claim.
    Returns parsed outcome.
    """
    api_key = get_api_key()
    if not api_key:
        logger.warning(f"Failed to check claim '{claim[:30]}...'. API Key not found.")
        return {"error": "API Key not found"}

    endpoint = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
    params = {
        "query": claim,
        "key": api_key
    }
    
    logger.info(f"Querying Google Fact Check API for claim: '{claim[:50]}'")
    
    try:
        response = requests.get(endpoint, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        claims = data.get("claims", [])
        if not claims:
            logger.info("No fact check result found for claim.")
            return None
            
        best_claim = claims[0]
        claim_reviews = best_claim.get("claimReview", [])
        
        if not claim_reviews:
            logger.info("Found claim but no claimReview present.")
            return None
            
        first_review = claim_reviews[0]
        publisher = first_review.get("publisher", {}).get("name", "Unknown Publisher")
        textual_rating = first_review.get("textualRating", "Unknown Rating")
        url = first_review.get("url", "#")
        
        logger.info(f"Fact check successful. Verdict: {textual_rating} by {publisher}")
        
        return {
            "claim": claim,
            "verdict": textual_rating,
            "publisher": publisher,
            "link": url
        }
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error querying Fact Check API: {e}")
        return None
    except ValueError as e:
        logger.error(f"JSON parsing error from Fact Check API: {e}")
        return None
    except Exception as e:
        logger.exception("Unexpected error in check_claim")
        return None

def fact_check_claims(claims: list[str]) -> list[dict]:
    """
    Runs fact checking for a list of claims.
    """
    results = []
    if not claims:
        return results
        
    logger.info(f"Starting fact checks for {len(claims)} claims.")
    for claim in claims:
        result = check_claim(claim)
        if result and "error" not in result:
            results.append(result)
        else:
            results.append({
                "claim": claim,
                "verdict": "No verified fact-check found",
                "publisher": "N/A",
                "link": None
            })
    logger.info("Completed fact checking for all claims.")
    return results
