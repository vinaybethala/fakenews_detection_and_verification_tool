import json
import os

SOURCES_FILE = "sources.json"
DEFAULT_SOURCES = ["Reuters Fact Check", "PolitiFact", "AP Fact Check", "Snopes", "BBC Verify"]

def _ensure_file():
    if not os.path.exists(SOURCES_FILE):
        with open(SOURCES_FILE, 'w') as f:
            json.dump(DEFAULT_SOURCES, f)

def get_sources() -> list[str]:
    _ensure_file()
    try:
        with open(SOURCES_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return DEFAULT_SOURCES

def add_source(source: str):
    sources = get_sources()
    if source and source not in sources:
        sources.append(source)
        with open(SOURCES_FILE, 'w') as f:
            json.dump(sources, f)

def remove_source(source: str):
    sources = get_sources()
    if source in sources:
        sources.remove(source)
        with open(SOURCES_FILE, 'w') as f:
            json.dump(sources, f)
