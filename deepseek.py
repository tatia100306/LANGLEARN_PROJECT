import os
import requests
from dotenv import load_dotenv

load_dotenv()

def tanya_ai(pertanyaan):
    api_key = os.getenv("GEMINI_API_KEY")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": pertanyaan
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(url, json=payload)

        data = response.json()

        return data["candidates"][0]["content"]["parts"][0]["text"]

    except Exception as e:
        return f"Error: {str(e)}"