const chat = document.getElementById("chat-box");
const input = document.getElementById("message");
const typing = document.getElementById("typing");

const BACKEND_URL = "https://vaidehi-chatbot-17mp.onrender.com";
const userId = localStorage.getItem("vaidehi_user_id");

// ===============================
// 🔊 CHAT SOUNDS
// ===============================
const sendSound = new Audio("assets/send.mp3");
const receiveSound = new Audio("assets/receive.mp3");
const giggleSound = new Audio("assets/giggling.mp3");
const crySound = new Audio("assets/crying.mp3");

// ===============================
// 🤭😢 REACTION RULES
// ===============================
function shouldGiggle(text) {
  const words = [
    "haha", "hehe", "😄", "😂",
    "ice", "icecream", "chocolate",
    "mummy", "mum", "maa"
  ];
  return words.some(w => text.toLowerCase().includes(w));
}

function shouldCry(text) {
  const words = [
    "ro", "cry", "sad", "daant",
    "gussa", "nahi", "maar"
  ];
  return words.some(w => text.toLowerCase().includes(w));
}

// ===============================
// 📜 LOAD CHAT HISTORY
// ===============================
async function loadHistory() {
  const res = await fetch(`${BACKEND_URL}/history?user_id=${userId}`);
  const data = await res.json();

  data.forEach(m => {
    chat.innerHTML += `
      <div class="${m.from === "user" ? "user" : "bot"}">
        <span>${escapeHTML(m.text)}</span>
      </div>`;
  });

  chat.scrollTop = chat.scrollHeight;
}

// ===============================
// 💬 SEND MESSAGE
// ===============================
async function sendMessage() {
  const msg = input.value.trim();
  if (!msg) return;

  // USER MESSAGE
  chat.innerHTML += `
    <div class="user">
      <span>${escapeHTML(msg)}</span>
    </div>`;
  chat.scrollTop = chat.scrollHeight;

  input.value = "";
  typing.style.display = "block";

  // 🔊 SEND SOUND
  sendSound.currentTime = 0;
  sendSound.play().catch(() => {});

  try {
    const res = await fetch(`${BACKEND_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: msg,
        user_id: userId
      })
    });

    const data = await res.json();
    typing.style.display = "none";

    // BOT MESSAGE
    chat.innerHTML += `
      <div class="bot">
        <span>${escapeHTML(data.reply)}</span>
      </div>`;
    chat.scrollTop = chat.scrollHeight;

    // 🔔 RECEIVE SOUND (FIRST)
    receiveSound.currentTime = 0;
    receiveSound.play().catch(() => {});

    // 🤭😢 AFTER RECEIVE SOUND FINISHES
    receiveSound.onended = () => {
      if (shouldCry(data.reply)) {
        crySound.currentTime = 0;
        crySound.play().catch(() => {});
      } else if (shouldGiggle(data.reply)) {
        giggleSound.currentTime = 0;
        giggleSound.play().catch(() => {});
      }
    };

  } catch (err) {
    typing.style.display = "none";
    console.error("Message send failed", err);
  }
}

// ===============================
// 🔐 SECURITY
// ===============================
function escapeHTML(t) {
  return t
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

// ===============================
// 🚪 LOGOUT
// ===============================
function logout() {
  localStorage.clear();
  location.href = "login.html";
}

// ===============================
// 🚀 ON LOAD
// ===============================
window.onload = () => {
  input.focus();
  loadHistory();
};
