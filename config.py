"""
Configuration module for GreenTrust AI.
Centralizes all application settings and constants.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project Paths
PROJECT_ROOT = Path(__file__).parent
DATA_SAMPLES_DIR = PROJECT_ROOT / "data_samples"
KNOWLEDGE_BASE_DIR = PROJECT_ROOT / "knowledge_base"
OUTPUT_DIR = PROJECT_ROOT / "output"

# Ensure output directory exists
OUTPUT_DIR.mkdir(exist_ok=True)

# LLM Configuration - Multi-Provider Support
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")  # Options: groq, gemini, openai
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")  # Default: Groq model
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.0"))
ENABLE_FALLBACK = os.getenv("ENABLE_FALLBACK", "true").lower() == "true"

# SEBI BRSR Compliance Thresholds
BRSR_THRESHOLDS = {
    "max_deviation_percent": 15.0,  # Maximum acceptable deviation from benchmark
    "min_trust_score": 60.0,  # Minimum acceptable trust score
    "data_quality_weight": 0.3,  # Weight for data quality in trust score
    "verification_weight": 0.4,  # Weight for verification results
    "disclosure_weight": 0.3,  # Weight for disclosure completeness
}

# Extraction Settings
EXTRACTION_CONFIG = {
    "chunk_size": 1000,  # Characters per chunk for LLM processing
    "overlap": 200,  # Overlap between chunks
    "max_pages": 50,  # Maximum pages to process per PDF
}

# Verification Settings
VERIFICATION_CONFIG = {
    "api_timeout": 5.0,  # Timeout for mock API calls (seconds)
    "retry_attempts": 3,  # Number of retry attempts for verification
}

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
