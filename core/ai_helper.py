# core/ai_helper.py
import logging
from groq import Groq
from django.conf import settings

logger = logging.getLogger(__name__)

_client = None

def get_groq_client():
    global _client
    if _client is None:
        api_key = settings.GROQ_API_KEY
        if not api_key:
            raise ValueError('GROQ_API_KEY is not configured')
        _client = Groq(api_key=api_key)
    return _client

# ========== FITUR 1: AI Conversation ==========
def ai_conversation(user_message):
    try:
        response = get_groq_client().chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": """You are a friendly English tutor named Grammify. 
                    Help users practice English conversation. 
                    Correct their grammar gently and encourage them to keep practicing.
                    Always respond in English but explain corrections in Indonesian if needed."""
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            max_tokens=500,
            temperature=0.7,
        )
        return {
            "success": True,
            "message": response.choices[0].message.content
        }
    except Exception as e:
        logger.exception('Groq AI conversation failed')
        return {
            "success": False,
            "message": "Maaf, layanan AI sedang tidak tersedia. Coba lagi ya! 🙏",
            "error": str(e) if settings.DEBUG else None
        }


# ========== FITUR 2: Grammar Checker ==========
def check_grammar(text):
    import json
    try:
        response = get_groq_client().chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": """You are a grammar checker. 
                    Analyze the given English text and respond ONLY in this JSON format, no extra text:
                    {
                        "corrected": "corrected version of the text",
                        "errors": [
                            {"original": "wrong part", "correction": "correct part", "explanation": "why in Indonesian"}
                        ],
                        "score": 85,
                        "feedback": "overall feedback in Indonesian"
                    }
                    If no errors, return empty errors array and score 100."""
                },
                {
                    "role": "user",
                    "content": f"Check this text: {text}"
                }
            ],
            max_tokens=800,
            temperature=0.3,
        )
        result = response.choices[0].message.content
        result = result.replace("```json", "").replace("```", "").strip()
        return {
            "success": True,
            "data": json.loads(result)
        }
    except Exception as e:
        return {
            "success": False,
            "message": "Gagal mengecek grammar. Coba lagi!"
        }