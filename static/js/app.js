const chatEl   = document.getElementById("chat");
const inputEl  = document.getElementById("input");
const sendBtn  = document.getElementById("sendBtn");
const voiceSel = document.getElementById("voiceSelect");
const micBtn   = document.getElementById("voiceToggle");

let voiceEnabled = true;
let availableVoices = [];
let currentAudio = null;

// Load voices (some browsers populate async)
function loadVoices() {
  availableVoices = window.speechSynthesis.getVoices();
}
window.speechSynthesis.onvoiceschanged = loadVoices;
loadVoices();

// ---------- Voice selection logic ----------
function pickVoice(profile) {
  if (!availableVoices.length) return null;

  // Preferred voice names per profile
  const preferred = {
    neutral:  ["Google UK English Female", "Samantha", "Karen", "Aria"],
    motherly: ["Karen", "Aria", "Google UK English Female", "Samantha"]
  };

  const names = preferred[profile] || preferred.neutral;

  for (const name of names) {
    const match = availableVoices.find(v => v.name.includes(name));
    if (match) return match;
  }
  // Fallback: any English voice
  return availableVoices.find(v => v.lang.startsWith("en")) || availableVoices[0];
}

async function speak(text, profile) {
  if (!voiceEnabled) return;

  try {
    const response = await fetch("/api/tts", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        text: text,
        voice_mode: profile
      })
    });

    if (!response.ok) {
      throw new Error("TTS request failed");
    }

    const audioBlob = await response.blob();
    const audioUrl = URL.createObjectURL(audioBlob);

    if (currentAudio) {
      currentAudio.pause();
      currentAudio.currentTime = 0;
    }

    const audio = new Audio(audioUrl);
    currentAudio = audio;

    audio.onended = () => {
      URL.revokeObjectURL(audioUrl);
    };

    await audio.play();

  } catch (err) {
    console.error("Voice error:", err);
  }
}

// ---------- UI helpers ----------
function addBubble(text, who, meta = "") {
  const div = document.createElement("div");
  div.className = `bubble ${who}`;
  div.innerHTML = `
    <div class="bubble-text">${escapeHtml(text)}</div>
    ${meta ? `<div class="bubble-meta">${meta}</div>` : ""}
  `;
  chatEl.appendChild(div);
  chatEl.scrollTop = chatEl.scrollHeight;
}

function addSpotCard(spot) {
  if (!spot) return;
  const card = document.createElement("div");
  card.className = "bubble ai";
  card.innerHTML = `
    <div class="spot-card">
      <strong>📍 ${spot.name}</strong><br/>
      <em>${spot.type}</em> — ${spot.vibe}<br/>
      About ${spot.distance_m} m away.
    </div>
  `;
  chatEl.appendChild(card);
  chatEl.scrollTop = chatEl.scrollHeight;
}

function escapeHtml(s) {
  return s.replace(/[&<>"']/g, c => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;",
    '"': "&quot;", "'": "&#39;"
  }[c]));
}

// ---------- Send message ----------
async function sendMessage() {
  const text = inputEl.value.trim();
  if (!text) return;
  const profile = voiceSel.value;

  addBubble(text, "user", "you");
  inputEl.value = "";

  try {
    // Optional: get user location if browser allows it
    const location = await getLocationSafe();

    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: text,
        voice_mode: profile,
        location
      })
    });

    const data = await res.json();
    addBubble(data.reply, "ai", "Calm Journey · just now");
    speak(data.reply, profile);

    if (data.spot) addSpotCard(data.spot);
  } catch (err) {
    addBubble(
      "I'm having a little trouble reaching my thoughts right now, but I'm still here with you.",
      "ai"
    );
  }
}

function getLocationSafe() {
  return new Promise(resolve => {
    if (!navigator.geolocation) return resolve(null);
    navigator.geolocation.getCurrentPosition(
      pos => resolve({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
      () => resolve(null),
      { timeout: 3000 }
    );
  });
}

sendBtn.addEventListener("click", sendMessage);
inputEl.addEventListener("keydown", e => {
  if (e.key === "Enter") sendMessage();
});

micBtn.addEventListener("click", () => {
  voiceEnabled = !voiceEnabled;
  micBtn.classList.toggle("muted", !voiceEnabled);

  if (!voiceEnabled && currentAudio) {
    currentAudio.pause();
    currentAudio.currentTime = 0;
  }
});
