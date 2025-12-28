import os
from dotenv import load_dotenv

load_dotenv()

PORT = int(os.getenv("PORT", 8001))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("⚠️  Warning: GEMINI_API_KEY not found in .env")
