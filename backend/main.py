from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from openai import OpenAI
import os, json, uuid

# =========================
# APP
# =========================
app = FastAPI()

# =========================
# CORS (Frontend allowed)
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
# OpenAI
# =========================
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# =========================
# MEMORY
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

LIKES:
Ice-cream 🍨
Chocolates 🍫
Rasmalai 😋

Always sound cute and emotional.
"""

# =========================
# CHAT API
# =========================
@app.post("/chat")
def chat(req: ChatRequest):
    user_id = req.user_id
    msg_lower = req.message.lower()

    # create memory
    if user_id not in user_memory:
        user_memory[user_id] = {
            "chat_history": []
        }

    user = user_memory[user_id]

    # -------------------------
    # SAVE NAME
    # -------------------------
    if "mera naam" in msg_lower:
        name = req.message.replace("mera naam", "").replace("hai", "").strip().capitalize()
        if name:
            user["name"] = name
            save_memory(user_memory)
            return {
                "reply": f"Aww 😄 main yaad rakhungi! Aapka naam {name} hai 💕"
            }

    # -------------------------
    # ASK NAME
    # -------------------------
    if "mera naam kya hai" in msg_lower:
        if "name" in user:
            return {"reply": f"Aapka naam {user['name']} hai 😄"}
        return {"reply": "Aapne abhi apna naam nahi bataya 😳"}

    # -------------------------
    # SAVE USER MESSAGE
    # -------------------------
    user["chat_history"].append({
        "from": "user",
        "text": req.message
    })

    # -------------------------
    # MEMORY CONTEXT
    # -------------------------
    memory_text = ""
    if "name" in user:
        memory_text = f"\nUser name is {user['name']}. Be extra loving."

    # -------------------------
    # AI CHAT
    # -------------------------
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT + memory_text},
            {"role": "user", "content": req.message}
        ]
    )

    reply = response.choices[0].message.content

    # save bot message
    user["chat_history"].append({
        "from": "vaidehi",
        "text": reply
    })

    # -------------------------
    # 🔊 TEXT → SPEECH (FIXED)
    # -------------------------
    audio_file = f"vaidehi_{uuid.uuid4()}.mp3"

    speech = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=reply
    )

    # ✅ CORRECT WAY
    speech.stream_to_file(audio_file)

    save_memory(user_memory)

    return {
        "reply": reply,
        "audio": audio_file
    }

# =========================
# AUDIO FILE SERVE
# =========================
@app.get("/audio/{filename}")
def get_audio(filename: str):
    return FileResponse(filename, media_type="audio/mpeg")

# =========================
# CHAT HISTORY
# =========================
@app.get("/history")
def history(user_id: str):
    return user_memory.get(user_id, {}).get("chat_history", [])
