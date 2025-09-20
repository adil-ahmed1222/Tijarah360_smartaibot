import os
from groq import Groq
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# Read GROQ API key strictly from environment
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY is not set. Please define it in your environment or .env file."
    )

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

def get_groq_response(prompt: str) -> str:
    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {
                    "role": "system",
                    "content": "You are Tijarah360 AI Assistant."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
        )
        return completion.choices[0].message.content or ""

    except Exception as e:
        print(f"❌ Groq API error: {e}")
        return "I apologize, but I'm having trouble processing your request right now."
