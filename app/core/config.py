from dotenv import load_dotenv
import os
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from sentence_transformers import SentenceTransformer
import cohere

# Load environment variables
load_dotenv()

class Settings:
    PROJECT_NAME: str = "Resume Matching LLM"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # API Keys and Credentials
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    COHERE_API_KEY: str = os.getenv("COHERE_API_KEY")
    ZILLZ_URI: str = os.getenv("ZILLZ_URI")
    ZILLZ_TOKEN: str = os.getenv("ZILLZ_TOKEN")

    # Model Configurations
    SENTENCE_TRANSFORMER_MODEL: str = 'all-MiniLM-L6-v2'
    GEMINI_MODEL: str = 'gemini-1.5-pro'
    GEMINI_TEMPERATURE: float = 0.0

    # CORS Configuration
    BACKEND_CORS_ORIGINS: list = ["*"]

settings = Settings()

# Initialize AI Models and Clients
genai.configure(api_key=settings.GEMINI_API_KEY)
embedder = SentenceTransformer(settings.SENTENCE_TRANSFORMER_MODEL)
cohere_client = cohere.Client(settings.COHERE_API_KEY)

# Gemini Safety Settings
GEMINI_SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE
} 