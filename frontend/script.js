const chat = document.getElementById("chat-box");
const input = document.getElementById("message");
const typing = document.getElementById("typing");

const BACKEND_URL = "https://vaidehi-chatbot-17mp.onrender.com";

const userId = localStorage.getItem("vaidehi_user_id");

// Load history
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

async function sendMessage() {
  const msg = input.value.trim();
  if (!msg) return;

  chat.innerHTML += `
    <div class="user"><span>${escapeHTML(msg)}</span></div>`;
  input.value = "";
  typing.style.display = "block";

  const res = await fetch(`${BACKEND_URL}/chat`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ message: msg, user_id: userId })
  });

  const data = await res.json();
  typing.style.display = "none";

  chat.innerHTML += `
    <div class="bot"><span>${escapeHTML(data.reply)}</span></div>`;

  chat.scrollTop = chat.scrollHeight;
}

function escapeHTML(t) {
  return t.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
}

function logout() {
  localStorage.clear();
  location.href = "login.html";
}

window.onload = loadHistory;
