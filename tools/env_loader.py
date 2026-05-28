import os
from dotenv import load_dotenv
import httpx

load_dotenv()

GROK_API_KEY = os.getenv("GROK_API_KEY")
GROK_MODEL = os.getenv("GROK_MODEL", "grok-4.3")

if not GROK_API_KEY:
    raise ValueError("Missing GROK_API_KEY in .env")

def call_grok(prompt):
    url = "https://api.x.ai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": GROK_MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.1,
        "max_tokens": 200
    }

    with httpx.Client(timeout=30.0) as client:
        response = client.post(url, json=data, headers=headers)
        response.raise_for_status()

        result = response.json()

        return result["choices"][0]["message"]["content"]

print("✅ Grok loader ready")
