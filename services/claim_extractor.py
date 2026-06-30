import re
from utils.logger import get_logger

logger = get_logger(__name__)

def extract_claims(text: str) -> list:
    """
    Extracts up to 3 factual claims from the given text.
    Preserves numbers, %, $ and other numeric symbols in claims.
    """
    if not text:
        logger.warning("Empty text passed to extract_claims.")
        return []

    logger.info("Starting claim extraction.")

    # Split on sentence boundaries — keep the delimiter attached via lookbehind
    sentences = re.split(r'(?<=[.!?])\s+', text)
    logger.info(f"Split text into {len(sentences)} sentences.")

    reporting_verbs = [
        'said', 'reported', 'confirmed', 'announced', 'claimed',
        'stated', 'revealed', 'warned', 'noted', 'found'
    ]
    entity_keywords = [
        'government', 'ministry', 'officials', 'country', 'agency',
        'report', 'study', 'data', 'president', 'police', 'court',
        'company', 'research', 'scientist', 'hospital', 'university'
    ]

    # Pattern that correctly matches:
    #   123   /   7.2%   /   $50   /   $3.5   /   million / billion / trillion
    quantitative_pattern = re.compile(
        r'\b\d+(\.\d+)?%\b'        # e.g. 7.2%  or 30%
        r'|\$\d+(\.\d+)?'          # e.g. $5  or $3.5
        r'|\b\d+(\.\d+)?\b'        # plain numbers
        r'|\b(million|billion|trillion)\b',
        re.IGNORECASE
    )

    scored_sentences = []

    for sentence in sentences:
        sentence = sentence.strip()

        # Filter out too-short or too-long sentences
        if len(sentence) < 30 or len(sentence) > 350:
            continue

        score = 0
        sentence_lower = sentence.lower()

        if any(verb in sentence_lower for verb in reporting_verbs):
            score += 2

        if any(kw in sentence_lower for kw in entity_keywords):
            score += 2

        # Search original sentence to correctly detect 7.2% etc.
        if quantitative_pattern.search(sentence):
            score += 3

        if score > 0:
            scored_sentences.append((score, sentence))

    scored_sentences.sort(key=lambda x: x[0], reverse=True)

    claims = []
    seen = set()
    for score, sentence in scored_sentences:
        if sentence not in seen:
            seen.add(sentence)
            claims.append(sentence)
        if len(claims) == 3:
            break

    # Fallback: return first valid sentence if no scored claims found
    if not claims:
        logger.info("No strong claims found. Applying fallback logic.")
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) >= 30:
                claims.append(sentence)
                break

    logger.info(f"Extraction complete. Found {len(claims)} claims.")
    return claims