const chat = document.getElementById("chat-box");
const input = document.getElementById("message");
const typing = document.getElementById("typing");

// 🔊 Sounds
const sendSound = new Audio("assets/send.mp3");
const receiveSound = new Audio("assets/receive.mp3");

// 🔗 BACKEND URL (Render)
const BACKEND_URL = "https://vaidehi-chatbot-17mp.onrender.com/chat";
// Local test:
// const BACKEND_URL = "http://127.0.0.1:8000/chat";

// ===============================
// 👤 WhatsApp-style USER ID
// ===============================
let userId = localStorage.getItem("vaidehi_user_id");

if (!userId) {
  userId = "user_" + Date.now() + "_" + Math.floor(Math.random() * 1000);
  localStorage.setItem("vaidehi_user_id", userId);
  console.log("New user_id created:", userId);
} else {
  console.log("Existing user_id:", userId);
}

// ===============================
// 💬 Send Message
// ===============================
async function sendMessage() {
  const msg = input.value.trim();
  if (!msg) return;

  // Show user message
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
      body: JSON.stringify({
        message: msg,
        user_id: userId   // ✅ VERY IMPORTANT
      })
    });

    const data = await res.json();

    // Fake typing delay
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
    console.error(error);
    typing.style.display = "none";
    chat.innerHTML += `
      <div class="bot">
        <span>Oops 😢 Vaidehi abhi baat nahi kar paa rahi…</span>
      </div>
    `;
  }
}

// ===============================
// 🔐 Prevent XSS
// ===============================
function escapeHTML(text) {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

// ===============================
// ⌨️ UX helpers
// ===============================
window.onload = () => {
  input.focus();
};

// Enter key support
input.addEventListener("keypress", function (e) {
  if (e.key === "Enter") {
    sendMessage();
  }
});
