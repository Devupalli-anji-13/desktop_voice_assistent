
import os
from dotenv import load_dotenv

load_dotenv()

# Groq: voice command interpretation
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL = "openai/gpt-oss-20b"

# KIE.ai: general AI conversations
KIE_API_KEY = os.getenv("KIE_API_KEY", "").strip()
KIE_BASE_URL = "https://api.kie.ai"
KIE_API_ENDPOINT = f"{KIE_BASE_URL}/codex/v1/responses"
KIE_MODEL_NAME = "gpt-6-astra"

SYSTEM_INSTRUCTIONS = """
You are JARVIS, a professional personal AI assistant.
Address the user politely.
Give clear, accurate and helpful answers.
Be concise unless the user requests detail.
You cannot directly control the user's computer.
"""
