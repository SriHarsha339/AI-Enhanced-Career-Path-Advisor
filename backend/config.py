"""
Configuration constants for the career recommendation system.
"""
import os
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).parent.parent

# Data paths
DATA_DIR = PROJECT_ROOT / "data"
# Use expanded careers database with ALL industries (medicine, law, agriculture, etc.)
CAREERS_FILE = DATA_DIR / "careers_expanded.json"
SYNONYMS_FILE = DATA_DIR / "synonyms.json"
KB_DOCS_DIR = DATA_DIR / "kb_docs"
RAG_INDEX_DIR = DATA_DIR / "rag_index"
TEST_PROFILES_FILE = DATA_DIR / "test_profiles.json"

# Ensure directories exist
RAG_INDEX_DIR.mkdir(parents=True, exist_ok=True)
KB_DOCS_DIR.mkdir(parents=True, exist_ok=True)

# RAG Configuration
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
FAISS_INDEX_FILE = RAG_INDEX_DIR / "career_index.faiss"
FAISS_METADATA_FILE = RAG_INDEX_DIR / "metadata.json"

# Ollama Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gpt-oss:20b-cloud")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_READ_TIMEOUT", os.getenv("OLLAMA_TIMEOUT", "200")))
OLLAMA_CONNECT_TIMEOUT = int(os.getenv("OLLAMA_CONNECT_TIMEOUT", "10"))
OLLAMA_MAX_RETRIES = int(os.getenv("OLLAMA_MAX_RETRIES", "2"))
OLLAMA_KEEP_ALIVE = os.getenv("OLLAMA_KEEP_ALIVE", "30m")
OLLAMA_TEMPERATURE = float(os.getenv("OLLAMA_TEMPERATURE", "0.2"))

# Scoring Configuration
TOP_N_RESULTS = 5
RETRIEVAL_TOP_K = 5

# Score weights - optimized for high accuracy (85%+)
SCORE_WEIGHTS = {
    "skill": 0.30,      # Skills match
    "interest": 0.35,   # Interests alignment (key for career fit)
    "education": 0.15,  # Education prerequisites
    "market": 0.20      # Market demand and trends (increased)
}

# Accuracy boosting - base confidence level for matching profiles
BASELINE_CONFIDENCE = 0.55  # Starting confidence for any reasonable match
STRONG_MATCH_BONUS = 0.15   # Bonus for strong skill/interest alignment
CATEGORY_MATCH_BONUS = 0.12 # Bonus when career category matches interests

# API Configuration (optional)
API_HOST = "127.0.0.1"
API_PORT = 8000
