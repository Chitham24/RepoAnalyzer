"""
Configuration module for RepoAnalyzer.
Loads environment variables and exposes project settings.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# GitHub Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_API_BASE_URL = os.getenv("GITHUB_API_BASE_URL", "https://api.github.com")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "60"))

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq").lower()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "")
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "1000"))
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))