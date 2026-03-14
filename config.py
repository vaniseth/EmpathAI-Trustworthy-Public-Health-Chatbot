import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- API Keys ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment.")


# --- LLM Provider Config ---
DEFAULT_GENERATIVE_LLM_PROVIDER = "google"

# Google Gemini
DEFAULT_GOOGLE_MODEL_ID = "gemini-2.5-flash"
DEFAULT_GOOGLE_GENERATION_CONFIG = {
    "temperature": 0.5,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}
DEFAULT_GOOGLE_EMBEDDING_MODEL = "gemini-embedding-001" # text-embedding-004

# --- Default Paths ---
DEFAULT_LOG_PATH = "logs/chatbot.log"
DEFAULT_FEEDBACK_PATH = "logs/feedback.csv"
DEFAULT_FLAGGED_PROMPTS_PATH = "logs/flagged_prompts.csv"
DEFAULT_VECTOR_DB_PATH = "knowledge_base_embeddings.csv"

# --- Default RAG Settings
DEFAULT_VECTOR_DB_TYPE = "csv" 
DEFAULT_CHUNK_STRATEGY = "recursive"
DEFAULT_CHUNK_SIZE = 512
DEFAULT_CHUNK_OVERLAP = 50
DEFAULT_TOP_K = 5
