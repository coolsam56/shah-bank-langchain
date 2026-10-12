import os
from dotenv import load_dotenv

load_dotenv()

BANK_NAME = os.getenv("BANK_NAME", "DemoBank")
PERSONAL_LOAN_ANNUAL_RATE = float(
    os.getenv("PERSONAL_LOAN_ANNUAL_RATE", "10.5")
)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv(
    "OPENAI_BASE_URL",
    "https://openrouter.ai/api/v1"
)
MODEL_NAME = os.getenv("MODEL_NAME", "")
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")