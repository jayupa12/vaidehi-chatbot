const chat = document.getElementById("chat-box");
const input = document.getElementById("message");
const typing = document.getElementById("typing");

const BACKEND_URL = "https://vaidehi-chatbot-17mp.onrender.com";

const userId = localStorage.getItem("vaidehi_user_id");

// ===============================
// 🔊 PLAY AUDIO FUNCTION
// ===============================
function playVoice(audioFile) {
  if (!audioFile) return;

  const audio = new Audio(`${BACKEND_URL}/audio/${audioFile}`);
  audio.play().catch(err => {
    console.log("Audio play blocked by browser", err);
  });
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

  // show user message
  chat.innerHTML += `
    <div class="user">
      <span>${escapeHTML(msg)}</span>
    </div>`;
  input.value = "";
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

    // show bot message
    chat.innerHTML += `
      <div class="bot">
        <span>${escapeHTML(data.reply)}</span>
      </div>`;

    chat.scrollTop = chat.scrollHeight;

    // 🔊 PLAY VAIDEHI VOICE
    if (data.audio) {
      playVoice(data.audio);
    }

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
    .replace(/&/g,"&amp;")
    .replace(/</g,"&lt;")
    .replace(/>/g,"&gt;");
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
