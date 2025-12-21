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
// 🎤 SPEECH RECOGNITION (CALL)
// ===============================
const SpeechRecognition =
  window.SpeechRecognition || window.webkitSpeechRecognition;

let recognition = null;
let callActive = false;

if (SpeechRecognition) {
  recognition = new SpeechRecognition();
  recognition.lang = "hi-IN";
  recognition.interimResults = false;
  recognition.continuous = true;
}

// ===============================
// 🤭😢 REACTION RULES
// ===============================
function shouldGiggle(text) {
  const words = [
    "haha", "hehe", "😂", "😄",
    "ice", "icecream", "ice-cream",
    "chocolate", "choclate",
    "mummy", "mum", "maa"
  ];
  return words.some(w => text.toLowerCase().includes(w));
}

function shouldCry(text) {
  const words = [
    "ro", "cry", "sad", "daant",
    "gussa", "nahi", "maar",
    "chup", "bad"
  ];
  return words.some(w => text.toLowerCase().includes(w));
}

// ===============================
// 🔊 PLAY ELEVENLABS VOICE
// ===============================
function playVaidehiVoice(audioFile) {
  if (!audioFile) return;

  const voice = new Audio(`${BACKEND_URL}/audio/${audioFile}`);
  voice.play().catch(err => {
    console.log("Voice autoplay blocked", err);
  });
}

// ===============================
// 📜 LOAD CHAT HISTORY
// ===============================
async function loadHistory() {
  try {
    const res = await fetch(`${BACKEND_URL}/history?user_id=${userId}`);
    const data = await res.json();

    data.forEach(m => {
      chat.innerHTML += `
        <div class="${m.from === "user" ? "user" : "bot"}">
          <span>${escapeHTML(m.text)}</span>
        </div>`;
    });

    chat.scrollTop = chat.scrollHeight;
  } catch (e) {
    console.error("History load failed", e);
  }
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
  typing.innerText = "Vaidehi is typing…";

  sendSound.currentTime = 0;
  sendSound.play().catch(() => {});

  try {
    const res = await fetch(`${BACKEND_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: msg, user_id: userId })
    });

    const data = await res.json();
    typing.style.display = "none";

    // BOT MESSAGE
    chat.innerHTML += `
      <div class="bot">
        <span>${escapeHTML(data.reply)}</span>
      </div>`;
    chat.scrollTop = chat.scrollHeight;

    // 🔔 RECEIVE SOUND
    receiveSound.currentTime = 0;
    receiveSound.play().catch(() => {});

    // CLEAR OLD HANDLER
    receiveSound.onended = null;

    // AFTER RECEIVE → EMOTION → VOICE
    receiveSound.onended = () => {

      if (shouldCry(data.reply)) {
        crySound.currentTime = 0;
        crySound.play().catch(() => {});
      }
      else if (shouldGiggle(data.reply)) {
        giggleSound.currentTime = 0;
        giggleSound.play().catch(() => {});
      }

      // 🎤 ELEVENLABS BACCHI VOICE (LAST)
      if (data.audio) {
        setTimeout(() => {
          playVaidehiVoice(data.audio);
        }, 300);
      }
    };

  } catch (err) {
    typing.style.display = "none";
    console.error("Message send failed", err);
  }
}

// ===============================
// 📞 CALL TOGGLE
// ===============================
function toggleCall() {
  const btn = document.querySelector(".call-btn");

  if (!recognition) {
    alert("Mic support nahi hai 😢");
    return;
  }

  if (!callActive) {
    callActive = true;
    btn.classList.add("active");
    btn.innerText = "📴";

    typing.style.display = "block";
    typing.innerText = "📞 Call connected… Vaidehi sun rahi hai";

    recognition.start();

    recognition.onresult = (event) => {
      const last = event.results.length - 1;
      const speechText = event.results[last][0].transcript;

      input.value = speechText;
      sendMessage();
    };

    recognition.onerror = stopCall;

  } else {
    stopCall();
  }
}

// ===============================
// ❌ END CALL
// ===============================
function stopCall() {
  callActive = false;
  if (recognition) recognition.stop();

  const btn = document.querySelector(".call-btn");
  if (btn) {
    btn.classList.remove("active");
    btn.innerText = "📞";
  }

  typing.style.display = "none";
  input.value = "";
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
