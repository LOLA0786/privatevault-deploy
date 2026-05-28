import os
from dotenv import load_dotenv
import httpx

load_dotenv()

GROK_API_KEY = os.getenv("GROK_API_KEY")

if not GROK_API_KEY:
    raise ValueError("Missing GROK_API_KEY in .env")


def call_grok(prompt):
    url = "https://api.x.ai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "grok-3-mini",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    with httpx.Client(timeout=30.0) as client:
        response = client.post(url, json=data, headers=headers)

        print("STATUS:", response.status_code)
        print("RESPONSE:", response.text)

        response.raise_for_status()

        result = response.json()

        return result["choices"][0]["message"]["content"]


print("✅ Grok loader ready")