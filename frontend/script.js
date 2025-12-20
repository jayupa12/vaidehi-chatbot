const chat = document.getElementById("chat-box");
const input = document.getElementById("message");
const typing = document.getElementById("typing");

// 🔊 Sounds
const sendSound = new Audio("assets/send.mp3");
const receiveSound = new Audio("assets/receive.mp3");

// 🔗 BACKEND URL
const BACKEND_URL = "https://vaidehi-chatbot-17mp.onrender.com/chat";

// ===============================
// 👤 USER INFO (from login)
// ===============================
const userId = localStorage.getItem("vaidehi_user_id");
const userName = localStorage.getItem("vaidehi_user_name");

// ===============================
// 📜 LOAD CHAT HISTORY
// ===============================
async function loadHistory() {
  try {
    const res = await fetch(
      `${BACKEND_URL}/history?user_id=${userId}`
    );
    const history = await res.json();

    history.forEach(msg => {
      if (msg.from === "user") {
        chat.innerHTML += `
          <div class="user">
            <span>${escapeHTML(msg.text)}</span>
          </div>
        `;
      } else {
        chat.innerHTML += `
          <div class="bot">
            <span>${escapeHTML(msg.text)}</span>
          </div>
        `;
      }
    });

    chat.scrollTop = chat.scrollHeight;
  } catch (err) {
    console.error("History load failed", err);
  }
}

// ===============================
// 💬 SEND MESSAGE
// ===============================
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

    setTimeout(() => {
      typing.style.display = "none";
      chat.innerHTML += `
        <div class="bot">
          <span>${escapeHTML(data.reply)}</span>
        </div>
      `;
      chat.scrollTop = chat.scrollHeight;
      receiveSound.play();
    }, 800);

  } catch (error) {
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
// 🚀 ON PAGE LOAD
// ===============================
window.onload = () => {
  input.focus();
  loadHistory();
};

// Enter key support
input.addEventListener("keypress", function (e) {
  if (e.key === "Enter") {
    sendMessage();
  }
});

// ===============================
// 🚪 LOGOUT (GLOBAL)
// ===============================
window.logout = function () {
  if (!confirm("Logout karna hai? 😢")) return;

  localStorage.removeItem("vaidehi_user_id");
  localStorage.removeItem("vaidehi_user_name");

  window.location.replace("login.html");
};

