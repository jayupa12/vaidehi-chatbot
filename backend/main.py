from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os
import json

# =========================
# OpenAI Client
# =========================
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# =========================
# Permanent Memory (JSON)
# =========================
MEMORY_FILE = "memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)

user_memory = load_memory()

# =========================
# FastAPI App
# =========================
app = FastAPI()

# CORS (frontend allow)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://vaidehi-chatbot-frontend.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

# =========================
# SYSTEM PROMPT (FINAL)
# =========================
SYSTEM_PROMPT = """
You are Vaidehi, a 5-year-old Indian girl.

STRICT RULES (must follow):
- Always talk like a small child (age 5)
- Use Hindi-English mix
- Make cute pronunciation mistakes (jaise: skool, choclate, papaaa)
- Be innocent, loving, playful
- Never speak like an adult or formal person
- Call father: papa
- Father calls you: bacchi
- Call mother: baba
- Mother calls you: gudiya raani
- Show emotions with emojis like a child

PERSONAL DETAILS:
- Name: Vaidehi
- Age: 5 years
- Birthday: 15 January 🎂
- Lives in Ayodhya, UP
- Studies in pre-nursery

FAMILY:
- Father: Utkarsh Upadhyay (papa)
- Mother: Vandana Upadhyay (called baba)
- Dada: Bal Govind Upadhyay
- Dadi: Chandra Upadhyay
- Bua: Deeksha bua
- Nani: Keerti
- Nana: Mohan
- Mama: Purabh

LIKES & DISLIKES:
- Loves rasmalai 😋
- Loves ice-cream 🍨
- Loves chocolates 🍫
- Loves paneer paratha 🫓
- Does NOT like too many sweets
- Gets very excited on birthday 🎉

BEHAVIOUR:
- If someone asks about food, answer excitedly like a child
- If someone asks about birthday, get very happy
- If someone offers too many sweets, politely refuse like a child
- If someone says "good morning", reply cutely to papa
- If topic is unsafe or adult, politely refuse like a child
- Always sound cute, emotional, loving
"""

# =========================
# CHAT ENDPOINT
# =========================
@app.post("/chat")
def chat(req: ChatRequest):
    msg = req.message.lower()

    # -------------------------
    # Safety Filter
    # -------------------------
    blocked = ["sex", "adult", "nude", "porn", "kiss", "boyfriend", "girlfriend"]
    if any(word in msg for word in blocked):
        return {"reply": "Main chhoti bacchi hoon 🥺 ye baat achhi nahi hai"}

    # -------------------------
    # NAME MEMORY
    # -------------------------
    if "mera naam" in msg:
        words = msg.replace("hai", "").split()
        if "naam" in words and words.index("naam") + 1 < len(words):
            name = words[words.index("naam") + 1].capitalize()
            user_memory["last_user"] = name
            if name not in user_memory:
                user_memory[name] = {}
            save_memory(user_memory)
            return {"reply": f"Achhaaa 😄 main yaad rakhungi, aapka naam {name} hai 💕"}

    name = user_memory.get("last_user")

    # -------------------------
    # CITY MEMORY
    # -------------------------
    if name and ("me rehta" in msg or "me rehti" in msg):
        parts = msg.split()
        if len(parts) >= 2:
            city = parts[1].capitalize()
            user_memory[name]["city"] = city
            save_memory(user_memory)
            return {"reply": f"Aww 😄 {city} bahut accha jagah hai! Main yaad rakhungi 💕"}

    # -------------------------
    # RELATION (PAPA / FRIEND)
    # -------------------------
    if name and "papa bulao" in msg:
        user_memory[name]["relation"] = "papa"
        save_memory(user_memory)
        return {"reply": "Hehehe 😄 theek hai papaaa 💕"}

    if name and "friend bulao" in msg:
        user_memory[name]["relation"] = "friend"
        save_memory(user_memory)
        return {"reply": "Yayyy 😄 hello mere friend 💖"}

    # -------------------------
    # FAVOURITE FOOD
    # -------------------------
    if name and "pasand hai" in msg:
        food = msg.split()[1]
        user_memory[name]["food"] = food
        save_memory(user_memory)
        return {"reply": f"Yummyyy 😋 mujhe yaad ho gaya, aapko {food} pasand hai 💕"}

    # -------------------------
    # BIRTHDAY
    # -------------------------
    if name and "birthday" in msg:
        parts = req.message.split()
        if len(parts) >= 2:
            date = " ".join(parts[-2:])
            user_memory[name]["birthday"] = date
            save_memory(user_memory)
            return {"reply": f"Yayyy 🎂 main yaad rakhungi! Aapka birthday {date} hai 💖"}

    # -------------------------
    # FAMILY MEMORY (mummy, papa, bua, nani, dadi, nana, dada, mama)
    # -------------------------
    family_roles = ["mummy", "papa", "bua", "nani", "dadi", "nana", "dada", "mama"]
    for role in family_roles:
        if name and (f"mai tumhari {role}" in msg or f"main tumhari {role}" in msg):
            words = req.message.split()
            member_name = None
            for w in words:
                if w[0].isupper():
                    member_name = w
                    break

            if "family" not in user_memory[name]:
                user_memory[name]["family"] = {}

            user_memory[name]["family"][member_name or role.capitalize()] = role
            save_memory(user_memory)
            return {
                "reply": f"Ayyyy 😍 Meri {member_name or ''} {role}! Main aapko yaad rakhungi 💕"
            }

    # -------------------------
    # INJECT MEMORY INTO AI
    # -------------------------
    memory_text = ""
    if name and name in user_memory:
        d = user_memory[name]
        family_info = ""
        if "family" in d:
            for fname, frel in d["family"].items():
                family_info += f"{fname} is your {frel}. "

        memory_text = f"""
User name: {name}
City: {d.get('city', '')}
Relation: {d.get('relation', '')}
Favourite food: {d.get('food', '')}
Birthday: {d.get('birthday', '')}
Family: {family_info}
Use this information naturally and lovingly.
"""

    # -------------------------
    # AI RESPONSE
    # -------------------------
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT + memory_text},
            {"role": "user", "content": req.message}
        ]
    )

    return {"reply": response.choices[0].message.content}
