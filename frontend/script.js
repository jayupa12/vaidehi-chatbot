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

// reactions
const giggleSound = new Audio("assets/giggling.mp3");
const crySound = new Audio("assets/crying.mp3");

// ===============================
// 🎤 BACCHI VOICE (Browser TTS)
// ===============================
function speakLikeVaidehi(text) {
  if (!window.speechSynthesis) return;

  speechSynthesis.cancel(); // stop previous

  const utter = new SpeechSynthesisUtterance(text);

  const voices = speechSynthesis.getVoices();
  const softGirl = voices.find(v =>
    v.name.toLowerCase().includes("female") ||
    v.name.toLowerCase().includes("girl")
  );

  if (softGirl) utter.voice = softGirl;

  utter.rate = 0.85;   // slow = cute
  utter.pitch = 1.4;  // high pitch = bacchi
  utter.volume = 1;

  speechSynthesis.speak(utter);
}

// ===============================
// 🤭😢 REACTION LOGIC
// ===============================
function shouldGiggle(text) {
  const words = [
    "haha", "hehe", "😂", "😄",
    "ice", "icecream", "chocolate",
    "mummy", "mum", "maa"
  ];
  return words.some(w => text.toLowerCase().includes(w));
}

function shouldCry(text) {
  const words = [
    "cry", "ro", "sad", "daant",
    "gussa", "nahi", "maar"
  ];
  return words.some(w => text.toLowerCase().includes(w));
}

function playGiggle() {
  giggleSound.currentTime = 0;
  giggleSound.play().catch(() => {});
}

function playCry() {
  crySound.currentTime = 0;
  crySound.play().catch(() => {});
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

    // 🔊 RECEIVE SOUND
    receiveSound.currentTime = 0;
    receiveSound.play().catch(() => {});

    // 🤭 / 😢 reaction first
    if (shouldCry(data.reply)) {
      setTimeout(playCry, 300);
    } else if (shouldGiggle(data.reply)) {
      setTimeout(playGiggle, 300);
    }

    // 🎤 bacchi voice
    setTimeout(() => {
      speakLikeVaidehi(data.reply);
    }, 700);

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
