import os
from openai import AsyncOpenAI 
from dotenv import load_dotenv

load_dotenv()

AI_MODEL = "gpt-4o" 


client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))