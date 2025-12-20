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
# Fixed Parent Truth (RULE)
# =========================
PARENT_MAP = {
    "Utkarsh": "papa",
    "Vandana": "mummy"
}

# =========================
# FastAPI App
# =========================
app = FastAPI()

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
# SYSTEM PROMPT
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
    # NAME MEMORY (SMART)
    # -------------------------
    if (("mera naam" in msg and "kya" not in msg) or "my name is" in msg):
        if "mera naam" in msg:
            words = msg.replace("hai", "").split()
            name = words[words.index("naam") + 1].capitalize()
        else:
            name = msg.split("my name is")[-1].strip().capitalize()

        user_memory["last_user"] = name

        if name not in user_memory:
            user_memory[name] = {}

        # ⭐ AUTO PARENT DETECTION
        if name in PARENT_MAP:
            role = PARENT_MAP[name]
            user_memory[name]["relation"] = role
            user_memory[name]["family"] = {name: role}
            save_memory(user_memory)
            return {
                "reply": f"Ayyyy 😍 Mere {role} {name}! Main aapse bahut pyaar karti hoon 💕"
            }

        save_memory(user_memory)
        return {
            "reply": f"Achhaaa 😄 main yaad rakhungi, aapka naam {name} hai 💕"
        }

    name = user_memory.get("last_user")

    # -------------------------
    # WHO AM I
    # -------------------------
    if name and ("mai kon hu" in msg or "mai kaun hu" in msg or "who am i" in msg):
        data = user_memory.get(name, {})
        if "relation" in data:
            return {
                "reply": f"Ayyyy 😄 Aap mere {data['relation']} ho, {name} 💕"
            }
        return {"reply": f"Aap {name} ho 😄"}

    # -------------------------
    # FAMILY ROLE MEMORY
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
    # WHAT IS MY NAME
    # -------------------------
    if name and ("mera naam kya hai" in msg or "what is my name" in msg):
        return {
            "reply": f"Aapka naam {name} hai 😄💕"
        }

    # -------------------------
    # AI MEMORY INJECTION
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
Relation: {d.get('relation', '')}
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
