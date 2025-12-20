const chat = document.getElementById("chat-box");
const input = document.getElementById("message");
const typing = document.getElementById("typing");

// 🔊 Sounds
const sendSound = new Audio("assets/send.mp3");
const receiveSound = new Audio("assets/receive.mp3");

// 🔗 BACKEND
const BACKEND_URL = "https://vaidehi-chatbot-17mp.onrender.com";

// 👤 USER (ONLY HERE)
const userId = localStorage.getItem("vaidehi_user_id");
const userName = localStorage.getItem("vaidehi_user_name");

// 🔐 LOGIN CHECK
if (!userId || !userName) {
  window.location.replace("login.html");
}

// 📜 LOAD HISTORY
async function loadHistory() {
  try {
    const res = await fetch(`${BACKEND_URL}/history?user_id=${userId}`);
    const history = await res.json();

    history.forEach(msg => {
      chat.innerHTML += `
        <div class="${msg.from === "user" ? "user" : "bot"}">
          <span>${escapeHTML(msg.text)}</span>
        </div>
      `;
    });

    chat.scrollTop = chat.scrollHeight;
  } catch (e) {
    console.error("History error", e);
  }
}

// 💬 SEND MESSAGE
async function sendMessage() {
  const msg = input.value.trim();
  if (!msg) return;

  chat.innerHTML += `
    <div class="user">
      <span>${escapeHTML(msg)}</span>
    </div>
  `;
  chat.scrollTop = chat.scrollHeight;

  input.value = "";
  sendSound.play();
  typing.style.display = "block";

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
    chat.innerHTML += `
      <div class="bot">
        <span>${escapeHTML(data.reply)}</span>
      </div>
    `;
    chat.scrollTop = chat.scrollHeight;
    receiveSound.play();

  } catch (e) {
    typing.style.display = "none";
    chat.innerHTML += `
      <div class="bot">
        <span>Oops 😢 Vaidehi abhi baat nahi kar paa rahi…</span>
      </div>
    `;
  }
}

// 🔐 XSS SAFE
function escapeHTML(text) {
  return text.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
}

// 🚀 LOAD
window.onload = () => {
  input.focus();
  loadHistory();
};

// ⏎ Enter key
input.addEventListener("keydown", e => {
  if (e.key === "Enter") sendMessage();
});

// 🚪 LOGOUT
function logout() {
  if (!confirm("Logout karna hai? 😢")) return;
  localStorage.clear();
  window.location.replace("login.html");
}
