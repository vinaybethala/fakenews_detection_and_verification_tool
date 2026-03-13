import re

SUSPICIOUS_KEYWORDS = [
    "miracle", "secret cure", "shocking truth", "government hiding", "suppressed", 
    "100% guaranteed", "scientists shocked", "breakthrough cure", "conspiracy", "hidden agenda"
]

def explain_claims(claims: list[str]) -> list[dict]:
    """
    Explainability MVP: Highlights suspicious words in each claim.
    Returns:
    [
      {
        "claim": str,
        "suspicious_words": list[str],
        "suspicious_score": float
      }
    ]
    """
    results = []
    
    for claim in claims:
        # Find exact matches case-insensitive
        lower_claim = claim.lower()
        found_words = []
        for kw in SUSPICIOUS_KEYWORDS:
            if kw in lower_claim:
                found_words.append(kw)
                
        # Calculate score (words matched / total words)
        total_words = len(claim.split()) if claim.strip() else 1
        score = len(found_words) / total_words if total_words > 0 else 0.0
        # Cap score to 1.0 (though count of found_words is usually <= total_words)
        score = min(score, 1.0)
        
        results.append({
            "claim": claim,
            "suspicious_words": found_words,
            "suspicious_score": round(score, 3)
        })
        
    return results
