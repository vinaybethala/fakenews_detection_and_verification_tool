from utils.logger import get_logger
from services.admin_manager import load_sources

logger = get_logger(__name__)

def check_source_trust(source_name: str) -> str:
    """
    Evaluates source trust against a dynamically loaded list of trusted publishers.
    """
    if not source_name or not source_name.strip():
        logger.info("Source check: No source provided.")
        return "Unverified"
        
    trusted_sources = load_sources()
    
    normalized_source = source_name.strip().lower()
    
    for trusted in trusted_sources:
        if trusted in normalized_source or normalized_source in trusted:
            logger.info(f"Source check: '{source_name}' marked as Trusted.")
            return "Trusted"
            
    logger.info(f"Source check: '{source_name}' marked as Unverified.")
    return "Unverified"
