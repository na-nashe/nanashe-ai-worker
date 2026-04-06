import os
from openai import OpenAI
from dotenv import load_dotenv

# Load system environment variables
load_dotenv()

def get_openai_key() -> str:
    """Retrieves OpenAI API Key and checks for its existence."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "Critical Error: OPENAI_API_KEY is not set. "
            "Please check your environment variables or .env file."
        )
    return api_key

# Initialize OpenAI client
client = OpenAI(api_key=get_openai_key())

# Use the current stable model
AI_MODEL = "gpt-4o-mini"