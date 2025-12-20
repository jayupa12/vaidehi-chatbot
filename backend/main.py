from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os

# OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 🧠 Simple in-memory user memory
user_memory = {}

app = FastAPI()

# ✅ CORS (frontend allow)
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


# ✅ EXACT SYSTEM PROMPT (AS YOU WANTED)
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


@app.post("/chat")
def chat(req: ChatRequest):
    user_id = "default"

    # 🧠 Learn user's name
    if "mera naam" in req.message.lower():
    words = req.message.lower().replace("hai", "").split()
    if "naam" in words:
        name_index = words.index("naam") + 1
        name = words[name_index].capitalize()
        user_memory[user_id] = name
        return {
            "reply": f"Achhaaa 😄 main yaad rakhungi, aapka naam {name} hai 💕"
        }

    # 🚫 Child safety filter
    blocked = ["sex", "adult", "nude", "porn", "kiss", "boyfriend", "girlfriend"]
    if any(word in req.message.lower() for word in blocked):
        return {
            "reply": "Main chhoti bacchi hoon 🥺 ye baat achhi nahi hai"
        }

    # 🧠 Add memory to prompt
    memory_text = ""
    if user_id in user_memory:
        memory_text = f" The user's name is {user_memory[user_id]}. Use it lovingly."

    # 🤖 AI response
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT + memory_text},
            {"role": "user", "content": req.message}
        ]
    )

    return {"reply": response.choices[0].message.content}

