import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_FACTCHECK_API_KEY", "")

def verify_claim(claim: str) -> dict:
    """
    Search Google Fact Check API for the claim.
    Returns parsed top result for verdict, publisher, url.
    Fallback to NOT_FOUND on no results or error.
    """
    fallback = {"claim": claim, "verdict": "NOT_FOUND", "publisher": "", "url": ""}
    
    if not API_KEY:
        print("Warning: No Google Fact Check API key provided.")
        return fallback

    url = f"https://factchecktools.googleapis.com/v1alpha1/claims:search"
    params = {
        "query": claim,
        "key": API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        claims = data.get("claims", [])
        if claims and len(claims) > 0:
            top_claim = claims[0]
            claim_reviews = top_claim.get("claimReview", [])
            if claim_reviews and len(claim_reviews) > 0:
                review = claim_reviews[0]
                return {
                    "claim": top_claim.get("text", claim),
                    "verdict": review.get("textualRating", "UNKNOWN"),
                    "publisher": review.get("publisher", {}).get("name", "Unknown Publisher"),
                    "url": review.get("url", "")
                }
        return fallback
    except Exception as e:
        print(f"Fact Check API error: {e}")
        return fallback
