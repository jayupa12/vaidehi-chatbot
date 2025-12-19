const chat = document.getElementById("chat-box");
const input = document.getElementById("message");
const typing = document.getElementById("typing");

// 🔊 Sounds
const sendSound = new Audio("assets/send.mp3");
const receiveSound = new Audio("assets/receive.mp3");

// 🔗 BACKEND URL (Render wala)
const BACKEND_URL = "https://vaidehi-backend.onrender.com/chat";
// Local test ke liye:
// const BACKEND_URL = "http://127.0.0.1:8000/chat";

async function sendMessage() {
  const msg = input.value.trim();
  if (!msg) return;

  // User message show
  chat.innerHTML += `
    <div class="user">
      <span>${escapeHTML(msg)}</span>
    </div>
  `;
  chat.scrollTop = chat.scrollHeight;

  input.value = "";
  sendSound.play();

  // Show typing indicator
  typing.style.display = "block";

  try {
    const res = await fetch(BACKEND_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ message: msg })
    });

    const data = await res.json();

    // Fake typing delay for realism
    setTimeout(() => {
      typing.style.display = "none";

      chat.innerHTML += `
        <div class="bot">
          <span>${escapeHTML(data.reply)}</span>
        </div>
      `;
      chat.scrollTop = chat.scrollHeight;
      receiveSound.play();
    }, 1200);

  } catch (error) {
    typing.style.display = "none";
    chat.innerHTML += `
      <div class="bot">
        <span>Oops 😢 Vaidehi abhi baat nahi kar paa rahi…</span>
      </div>
    `;
  }
}

// 🔐 Prevent XSS / HTML injection
function escapeHTML(text) {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

// Optional: Auto-focus input on load
window.onload = () => {
  input.focus();
};
