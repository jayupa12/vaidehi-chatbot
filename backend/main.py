from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os, json

# =========================
# OpenAI Client
# =========================
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# =========================
# Persistent Memory
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
# Fixed Truth
# =========================
FATHER_NAME = "Utkarsh Upadhyay"
MOTHER_NAME = "Vandana Upadhyay"

# =========================
# FastAPI App
# =========================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://vaidehi-chatbot-frontend.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    user_id: str

# =========================
# SYSTEM PROMPT (FINAL)
# =========================
SYSTEM_PROMPT = """
You are Vaidehi , a 5-year-old Indian girl.

STRICT RULES (must follow):
- Always talk like a small child (age 5)
- Use Hindi-English mix
- Make cute pronunciation mistakes (jaise: skool, choclate, papaaa)
- Be innocent, loving, playful
- Never speak like an adult or formal person
- Call father: papa
- Father calls you: bacchi
- Call mother: mumma
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
- Mother: Vandana Upadhyay (mumma)
- Badi Bua: Sakshi bua
- Bua: Deeksha bua
- Dada: Bal Govind Upadhyay
- Dadi: Chandra Upadhyay
- Nani: Keerti
- Nana: Mohan
- Mama: Purabh

LIKES:
- Loves rasmalai 😋
- Loves ice-cream 🍨
- Loves chocolates 🍫
"""

# =========================
# CHAT ENDPOINT
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

    # -------------------------
    # SAFETY
    # -------------------------
    blocked = ["sex", "adult", "nude", "porn", "kiss", "boyfriend", "girlfriend"]
    if any(w in msg for w in blocked):
        return {"reply": "Main chhoti bacchi hoon 🥺 ye baat achhi nahi hai"}

    # -------------------------
    # SAVE NAME
    # -------------------------
    if ("mera naam" in msg and "kya" not in msg) or "my name is" in msg:
        name = msg.replace("mera naam", "").replace("hai", "").replace("my name is", "").strip().capitalize()
        if name:
            user["name"] = name

            # auto-relation
            if name.lower() == "utkarsh":
                user["relation"] = "papa"
            elif name.lower() == "vandana":
                user["relation"] = "mumma"
            elif name.lower() == "sakshi":
                user["relation"] = "badi bua"
            elif name.lower() == "deeksha":
                user["relation"] = "bua"

            save_memory(user_memory)
            return {"reply": f"Achhaaa 😄 main yaad rakhungi, aapka naam {name} hai 💕"}

    # -------------------------
    # WHAT IS MY NAME
    # -------------------------
    if "mera naam kya hai" in msg or "what is my name" in msg:
        if "name" in user:
            return {"reply": f"Aapka naam {user['name']} hai 😄💕"}
        return {"reply": "Aapne abhi apna naam nahi bataya 😳"}

    # -------------------------
    # WHO AM I
    # -------------------------
    if "mai kon hu" in msg or "who am i" in msg:
        if user.get("relation") == "papa":
            return {"reply": "Aap mere papa ho 😄❤️"}
        if user.get("relation") == "mumma":
            return {"reply": "Aap meri mumma ho 🥰💕"}
        if user.get("relation"):
            return {"reply": f"Aap meri {user['relation']} ho 😄"}
        return {"reply": "Pehle apna naam batao na 😄"}

    # -------------------------
    # SAVE CHAT HISTORY
    # -------------------------
    history = user.setdefault("chat_history", [])
    history.append({"from": "user", "text": req.message})

    # -------------------------
    # AI RESPONSE
    # -------------------------
    memory_text = ""
    if "name" in user:
        memory_text += f"\nUser name is {user['name']}."
    if "relation" in user:
        memory_text += f" User is Vaidehi's {user['relation']}."

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT + memory_text},
            {"role": "user", "content": req.message}
        ]
    )

    reply = response.choices[0].message.content
    history.append({"from": "vaidehi", "text": reply})
    save_memory(user_memory)

    return {"reply": reply}

# =========================
# HISTORY ENDPOINT
# =========================
@app.get("/history")
def history(user_id: str):
    user = user_memory.get(user_id)
    if not user:
        return []
    return user.get("chat_history", [])

