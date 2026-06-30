import json
import os
from datetime import datetime
from utils.logger import get_logger

logger = get_logger(__name__)

# Absolute paths for safe file resolution relative to this file's location
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCES_FILE = os.path.join(BASE_DIR, "data", "sources.json")
LOGS_FILE = os.path.join(BASE_DIR, "data", "logs.json")

def ensure_file_exists(filepath: str, default_content):
    """Ensures a JSON file exists, creating it with default content if not."""
    if not os.path.exists(filepath):
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(default_content, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to create file {filepath}: {e}")

def load_sources() -> list:
    """Loads trusted sources from JSON."""
    ensure_file_exists(SOURCES_FILE, [])
    try:
        with open(SOURCES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load sources: {e}")
        return []

def save_sources(sources: list):
    """Saves trusted sources to JSON."""
    try:
        with open(SOURCES_FILE, 'w', encoding='utf-8') as f:
            json.dump(sources, f, indent=4)
        logger.info(f"Saved {len(sources)} sources to {SOURCES_FILE}")
    except Exception as e:
        logger.error(f"Failed to save sources: {e}")

def add_source(source: str) -> bool:
    """Adds a new source if it doesn't already exist."""
    sources = load_sources()
    norm_source = source.strip().lower()
    if norm_source and norm_source not in sources:
        sources.append(norm_source)
        save_sources(sources)
        return True
    return False

def remove_source(source: str) -> bool:
    """Removes a source."""
    sources = load_sources()
    norm_source = source.strip().lower()
    if norm_source in sources:
        sources.remove(norm_source)
        save_sources(sources)
        return True
    return False

def log_analysis(label: str, confidence: float, source_name: str, char_length: int):
    """Appends an analysis event to the logs."""
    ensure_file_exists(LOGS_FILE, [])
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "label": label,
        "confidence": confidence,
        "source": source_name if source_name else "Unknown",
        "char_length": char_length
    }
    try:
        with open(LOGS_FILE, 'r', encoding='utf-8') as f:
            logs = json.load(f)
        logs.append(log_entry)
        with open(LOGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=4)
    except Exception as e:
        logger.error(f"Failed to log analysis: {e}")

def get_logs() -> list:
    """Retrieves all logs."""
    ensure_file_exists(LOGS_FILE, [])
    try:
        with open(LOGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to read logs: {e}")
        return []

def get_analytics() -> dict:
    """Computes basic analytics from logs."""
    logs = get_logs()
    total = len(logs)
    real_count = sum(1 for log in logs if log.get("label") == "REAL")
    fake_count = sum(1 for log in logs if log.get("label") == "FAKE")
    unknown_count = total - real_count - fake_count
    
    return {
        "total": total,
        "real": real_count,
        "fake": fake_count,
        "unknown": unknown_count
    }
