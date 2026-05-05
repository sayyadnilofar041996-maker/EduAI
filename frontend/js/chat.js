// ============================================================
// chat.js — AI Teacher Chat Interface
// ============================================================

const API = "http://127.0.0.1:8000";

// ============================================================
// READ FROM LOCALSTORAGE
// ============================================================
const token   = localStorage.getItem("token");
const grade   = localStorage.getItem("grade");
const name    = localStorage.getItem("name");
const bookId  = localStorage.getItem("selected_book_id");
const subject = localStorage.getItem("selected_book_subject");
const title   = localStorage.getItem("selected_book_title");

// ============================================================
// PROTECT PAGE — redirect if not logged in
// ============================================================
if (!token || !bookId) {
  window.location.href = "/frontend/index.html";  // ✅ fixed
}

// ============================================================
// expose bookId to sidebar (chat.html reads this)
// ============================================================
window.currentBookId = bookId;

// ============================================================
// FILL PAGE INFO
// ============================================================
document.getElementById("user-greeting").textContent        = `Welcome, ${name}!`;
document.getElementById("book-title-display").textContent   = title;
document.getElementById("book-subject-display").textContent = subject;
document.getElementById("grade-display").textContent        = grade;

document.getElementById("welcome-text").textContent =
  `Hello ${name}! 👋 I am your ${subject} teacher. Ask me anything from your textbook!`;

// ============================================================
// HELPER — Add message to chat
// ============================================================
function addMessage(text, sender) {
  const messagesDiv = document.getElementById("chat-messages");

  const messageDiv = document.createElement("div");
  messageDiv.className = `message ${sender}-message`;

  const avatar = sender === "ai" ? "🤖" : "👤";

  messageDiv.innerHTML = `
    <div class="message-avatar">${avatar}</div>
    <div class="message-bubble">${formatMessage(text)}</div>
  `;

  messagesDiv.appendChild(messageDiv);
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// ============================================================
// HELPER — Format AI message text
// ============================================================
function formatMessage(text) {
  text = text.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
  text = text.replace(/\n/g, "<br>");
  return text;
}

// ============================================================
// HELPER — Show/hide typing indicator
// ============================================================
function showTyping() {
  const indicator = document.getElementById("typing-indicator");
  indicator.classList.remove("hidden");
  const messagesDiv = document.getElementById("chat-messages");
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function hideTyping() {
  document.getElementById("typing-indicator").classList.add("hidden");
}

// ============================================================
// HELPER — Enable/disable send button
// ============================================================
function setSendButton(enabled) {
  const btn   = document.getElementById("send-btn");
  const input = document.getElementById("question-input");
  btn.disabled   = !enabled;
  input.disabled = !enabled;
}

// ============================================================
// HANDLE ENTER KEY
// ============================================================
function handleKeyPress(event) {
  if (event.key === "Enter") {
    event.preventDefault();
    sendQuestion();
  }
}

// ============================================================
// MAIN — SEND QUESTION TO AI
// ============================================================
async function sendQuestion() {
  const input    = document.getElementById("question-input");
  const language = document.getElementById("lang-select").value;
  const question = input.value.trim();

  if (!question) return;

  addMessage(question, "student");
  input.value = "";

  setSendButton(false);
  showTyping();

  try {
    const response = await fetch(`${API}/chat/ask`, {
      method: "POST",
      headers: {
        "Content-Type":  "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify({
        subject:  subject,
        question: question,
        language: language,
        chapter:  window.sidebarState?.activeChapterName  || null,
        subtopic: window.sidebarState?.activeSubtopicName || null
      })
    });

    const data = await response.json();
    hideTyping();

    if (!response.ok) {
      addMessage("⚠️ Error: " + (data.detail || "Something went wrong."), "ai");
      setSendButton(true);
      return;
    }

    addMessage(data.ai_answer, "ai");

    if (data.doubt_detected) {
      setTimeout(() => {
        addMessage("🤔 I noticed you were confused. I changed my explanation style. Does this help?", "ai");
      }, 1000);
    }

  } catch (err) {
    hideTyping();
    console.error("Fetch error:", err);
    addMessage("❌ Cannot connect to server. Is FastAPI running?", "ai");
  }

  setSendButton(true);
}

// ============================================================
// GO BACK TO DASHBOARD
// ============================================================
function goBack() {
  window.location.href = "/frontend/dashboard.html";
}

// ============================================================
// LOGOUT
// ============================================================
function logout() {
  localStorage.clear();
  window.location.href = "/frontend/index.html";
}