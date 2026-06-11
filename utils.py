import os
import requests
from dotenv import load_dotenv

# Ambil data dari file .env
load_dotenv()

def panggil_ai_gemini(teks_user):
    api_key = os.getenv("GEMINI_API_KEY")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": teks_user
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(url, json=payload)
        data = response.json()

        # Mengambil jawaban teks dari AI Gemini
        return data["candidates"][0]["content"]["parts"][0]["text"]

    except Exception as e:
        return f"Waduh, ada masalah: {str(e)}"