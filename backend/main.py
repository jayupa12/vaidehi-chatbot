from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from openai import OpenAI
import requests
import os, json, uuid

# =========================
# APP
# =========================
app = FastAPI()

# =========================
# CORS
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://vaidehi-chatbot-frontend.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# KEYS (Render ENV)
# =========================
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
ELEVEN_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")

client = OpenAI(api_key=OPENAI_KEY)

# =========================
# MEMORY (JSON)
# =========================
MEMORY_FILE = "memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_memory(mem):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(mem, f, ensure_ascii=False, indent=2)

user_memory = load_memory()

# =========================
# REQUEST MODEL
# =========================
class ChatRequest(BaseModel):
    message: str
    user_id: str

# =========================
# SYSTEM PROMPT
# =========================
SYSTEM_PROMPT = """
You are Vaidehi, a 5-year-old Indian girl.

RULES:
- Talk like a small child
- Hindi-English mix
- Cute mistakes (choclate, skool)
- Innocent, loving, playful
- Use emojis
- Call father papa
- Call mother mumma

DETAILS:
Name: Vaidehi
Age: 5
Lives in Ayodhya

FAMILY:
Father: Utkarsh Upadhyay
Mother: Vandana Upadhyay
Badi Bua: Sakshi bua
Bua: Deeksha bua
Nana: Shri Mohan Bhardwaj
Nani: Shrimati Keerti Bhardwaj
Mama: Purab mama
Dada: Shri Balgovind Upadhyay
Dadi: Shrimati Chandra Upadhyay

LIKES:
Ice-cream 🍨
Chocolates 🍫
Rasmalai 😋

Nature:
Thodi ziddi, no patience, hide-and-seek lover

Always sound cute, emotional and childish.
"""

# =========================
# EMOTION DETECTOR
# =========================
def detect_emotion(text: str) -> str:
    t = text.lower()
    if any(w in t for w in ["hehe", "haha", "😂", "😄", "ice", "icecream", "chocolate", "mumma"]):
        return "giggle"
    if any(w in t for w in ["nahi", "ro", "cry", "sad", "gussa", "daant"]):
        return "cry"
    return "normal"

# =========================
# ELEVENLABS TTS (SAFE)
# =========================
def elevenlabs_tts(text: str):
    try:
        audio_file = f"vaidehi_{uuid.uuid4()}.mp3"

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
        headers = {
            "xi-api-key": ELEVEN_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.30,
                "similarity_boost": 0.85,
                "style": 0.9,
                "use_speaker_boost": True
            }
        }

        r = requests.post(url, json=payload, headers=headers, timeout=30)
        r.raise_for_status()

        with open(audio_file, "wb") as f:
            f.write(r.content)

        return audio_file

    except Exception as e:
        print("❌ ElevenLabs TTS failed:", e)
        return None

# =========================
# CHAT API
# =========================
@app.post("/chat")
def chat(req: ChatRequest):
    user_id = req.user_id

    if user_id not in user_memory:
        user_memory[user_id] = {"chat_history": []}

    user = user_memory[user_id]

    # Save user message
    user["chat_history"].append({
        "from": "user",
        "text": req.message
    })

    # GPT Response
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": req.message}
        ]
    )

    reply = response.choices[0].message.content
    emotion = detect_emotion(reply)

    # Save bot message
    user["chat_history"].append({
        "from": "vaidehi",
        "text": reply
    })
    save_memory(user_memory)

    # ElevenLabs Voice
    audio_file = elevenlabs_tts(reply)

    result = {
        "reply": reply,
        "emotion": emotion
    }

    if audio_file:
        result["audio"] = audio_file

    return result

# =========================
# AUDIO SERVE
# =========================
@app.get("/audio/{filename}")
def audio(filename: str):
    return FileResponse(filename, media_type="audio/mpeg")

# =========================
# CHAT HISTORY
# =========================
@app.get("/history")
def history(user_id: str):
    return user_memory.get(user_id, {}).get("chat_history", [])
