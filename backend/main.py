from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os, json

# =========================
# APP (FIRST THING)
# =========================
app = FastAPI()

# =========================
# CORS (VERY IMPORTANT)
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
# CONSTANT TRUTH
# =========================
FATHER_NAME = "Utkarsh Upadhyay"
MOTHER_NAME = "Vandana Upadhyay"

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
You are Vaidehi , a 5-year-old Indian girl.

STRICT RULES:
- Talk like a 5-year-old child
- Hindi-English mix
- Cute mistakes
- Innocent, loving
- Call father papa
- Call mother mumma
- Use emojis

PERSONAL:
Name: Vaidehi
Age: 5
Lives: Ayodhya

FAMILY:
Father: Utkarsh Upadhyay
Mother: Vandana Upadhyay
Badi Bua: Sakshi bua
Bua: Deeksha bua

Always be cute.
"""

# =========================
# CHAT API
# =========================
@app.post("/chat")
def chat(req: ChatRequest):
    user_id = req.user_id
    msg = req.message.lower()

    if user_id not in user_memory:
        user_memory[user_id] = {
            "chat_history": {}
        }

    user = user_memory[user_id]

    # Save name
    if "mera naam" in msg:
        name = req.message.split()[-1].capitalize()
        user["name"] = name
        save_memory(user_memory)
        return {"reply": f"Aww 😄 main yaad rakhungi! Aapka naam {name} hai 💕"}

    # Ask name
    if "mera naam kya hai" in msg:
        if "name" in user:
            return {"reply": f"Aapka naam {user['name']} hai 😄"}
        return {"reply": "Aapne abhi naam nahi bataya 😳"}

    # Save user message
    user["chat_history"].setdefault("messages", []).append({
        "from": "user",
        "text": req.message
    })

    memory_text = ""
    if "name" in user:
        memory_text = f"\nUser name is {user['name']}."

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT + memory_text},
            {"role": "user", "content": req.message}
        ]
    )

    reply = response.choices[0].message.content

    user["chat_history"]["messages"].append({
        "from": "vaidehi",
        "text": reply
    })

    save_memory(user_memory)
    return {"reply": reply}

# =========================
# HISTORY API
# =========================
@app.get("/history")
def history(user_id: str):
    return user_memory.get(user_id, {}).get("chat_history", {}).get("messages", [])
