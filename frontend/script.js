const chat = document.getElementById("chat-box");
const input = document.getElementById("message");
const typing = document.getElementById("typing");

// BACKEND ROOT (NO /chat here)
const BACKEND_URL = "https://vaidehi-chatbot-17mp.onrender.com";

const userId = localStorage.getItem("vaidehi_user_id");
const userName = localStorage.getItem("vaidehi_user_name");

// ===============================
// LOAD CHAT HISTORY
// ===============================
async function loadHistory() {
  try {
    const res = await fetch(`${BACKEND_URL}/history?user_id=${userId}`);
    const history = await res.json();

    history.forEach(m => {
      chat.innerHTML += `
        <div class="${m.from === "user" ? "user" : "bot"}">
          <span>${escapeHTML(m.text)}</span>
        </div>`;
    });

    chat.scrollTop = chat.scrollHeight;
  } catch {}
}

// ===============================
// SEND MESSAGE
// ===============================
async function sendMessage() {
  const msg = input.value.trim();
  if (!msg) return;

  chat.innerHTML += `
    <div class="user"><span>${escapeHTML(msg)}</span></div>`;
  chat.scrollTop = chat.scrollHeight;

  input.value = "";
  typing.style.display = "block";

  try {
    const res = await fetch(`${BACKEND_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: msg, user_id: userId })
    });

    const data = await res.json();

    setTimeout(() => {
      typing.style.display = "none";
      chat.innerHTML += `
        <div class="bot"><span>${escapeHTML(data.reply)}</span></div>`;
      chat.scrollTop = chat.scrollHeight;
    }, 700);

  } catch {
    typing.style.display = "none";
  }
}

// ===============================
function escapeHTML(text) {
  return text.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
}

// ===============================
function logout() {
  localStorage.clear();
  window.location.replace("login.html");
}

// ===============================
window.onload = () => {
  input.focus();
  loadHistory();
};
