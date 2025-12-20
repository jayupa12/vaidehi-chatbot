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
# Fixed Truth (Never Guess)
# =========================
FATHER_NAME = "Utkarsh Upadhyay"
MOTHER_NAME = "Vandana Upadhyay"

# =========================
# FastAPI App
# =========================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # public site
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    user_id: str

# =========================
# SYSTEM PROMPT (EXACT)
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
- Mother: Vandana Upadhyay (mumma)
- Dada: Bal Govind Upadhyay
- Dadi: Chandra Upadhyay
- Badi Bua: Sakshi bua
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
    user_id = req.user_id

    # create per-user memory
    if user_id not in user_memory:
        user_memory[user_id] = {}

    user_data = user_memory[user_id]

    # -------------------------
    # Safety
    # -------------------------
    blocked = ["sex", "adult", "nude", "porn", "kiss", "boyfriend", "girlfriend"]
    if any(w in msg for w in blocked):
        return {"reply": "Main chhoti bacchi hoon 🥺 ye baat achhi nahi hai"}

    # -------------------------
    # Rule-based facts
    # -------------------------
    if "tumhare papa ka naam" in msg:
        return {"reply": f"Mere papa ka naam {FATHER_NAME} hai 😄❤️"}

    if "tumhari mummy ka naam" in msg:
        return {"reply": f"Meri mummy ka naam {MOTHER_NAME} hai 😄💕"}

    # -------------------------
    # Save Name (only when telling)
    # -------------------------
    if ("mera naam" in msg and "kya" not in msg) or "my name is" in msg:
        if "mera naam" in msg:
            words = msg.replace("hai", "").split()
            if "naam" in words and words.index("naam") + 1 < len(words):
                name = words[words.index("naam") + 1].capitalize()
            else:
                name = None
        else:
            name = msg.split("my name is")[-1].strip().capitalize()

        if name:
            user_data["name"] = name
            save_memory(user_memory)
            return {"reply": f"Achhaaa 😄 main yaad rakhungi, aapka naam {name} hai 💕"}

    # -------------------------
    # What is my name?
    # -------------------------
    if "mera naam kya hai" in msg or "what is my name" in msg:
        if "name" in user_data:
            return {"reply": f"Aapka naam {user_data['name']} hai 😄💕"}
        return {"reply": "Aapne abhi apna naam nahi bataya 😳"}

    # -------------------------
    # Who am I? (no guessing)
    # -------------------------
    if "mai kon hu" in msg or "mai kaun hu" in msg or "who am i" in msg:
        return {"reply": "Pehle apna naam batao na 😄 phir main yaad rakhungi 💕"}

    # -------------------------
    # AI with per-user memory
    # -------------------------
    memory_text = ""
    if "name" in user_data:
        memory_text = f"\nUser name is {user_data['name']}. Be extra loving."

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT + memory_text},
            {"role": "user", "content": req.message}
        ]
    )

    return {"reply": response.choices[0].message.content}

