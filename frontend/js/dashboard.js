// ============================================================
// dashboard.js — Loads student's books from backend
// ============================================================

const API = "http://127.0.0.1:8000";

// ============================================================
// CONCEPT 1 — Read from localStorage
// ============================================================
const token = localStorage.getItem("token");
const grade = localStorage.getItem("grade");
const name  = localStorage.getItem("name");
const role  = localStorage.getItem("role");

// ============================================================
// CONCEPT 2 — Protect the page
// ============================================================
if (!token || token === "null" || token === "undefined") {
  window.location.href = "/frontend/index.html";
}

// ============================================================
// CONCEPT 3 — Update the UI with user info
// ============================================================
document.getElementById("user-greeting").textContent = `Welcome, ${name}!`;
document.getElementById("grade-label").textContent = `Grade ${grade} — Your Books`;

// ============================================================
// CONCEPT 4 — Book icons based on subject
// ============================================================
function getBookIcon(subject) {
  const icons = {
    math:      "📐",
    science:   "🔬",
    english:   "📖",
    history:   "🏛️",
    geography: "🌍",
    computer:  "💻",
    hindi:     "📝",
    marathi:   "📝",
    social:    "🌐",
    default:   "📚"
  };
  return icons[subject.toLowerCase()] || icons["default"];
}

// ============================================================
// CONCEPT 5 — Create a book card element
// ============================================================
function createBookCard(book) {
  const card = document.createElement("div");
  card.className = "book-card";

  card.innerHTML = `
    <span class="book-icon">${getBookIcon(book.subject)}</span>
    <div class="book-title">${book.title}</div>
    <div class="book-subject">${book.subject}</div>
    <div class="book-arrow">Tap to learn →</div>
  `;

  card.onclick = () => {
    localStorage.setItem("selected_book_id",     book.id);
    localStorage.setItem("selected_book_subject", book.subject);
    localStorage.setItem("selected_book_title",   book.title);
    window.location.href = "/frontend/chat.html";
  };

  return card;
}

// ============================================================
// CONCEPT 6 — Fetch books from backend
// ============================================================
async function loadBooks() {
  try {
    const response = await fetch(`${API}/books/${grade}`, {
      method: "GET",
      headers: { "Authorization": `Bearer ${token}` }
    });

    const books = await response.json();
    document.getElementById("loading-state").classList.add("hidden");

    if (!response.ok) {
      window.location.href = "/frontend/index.html";
      return;
    }

    if (books.length === 0) {
      document.getElementById("empty-state").classList.remove("hidden");
      return;
    }

    const grid = document.getElementById("books-grid");
    books.forEach(book => {
      const card = createBookCard(book);
      grid.appendChild(card);
    });

  } catch (err) {
    document.getElementById("loading-state").textContent =
      "Cannot connect to server. Is FastAPI running?";
  }
}

// ============================================================
// GO TO PROGRESS PAGE
// ============================================================
function goToProgress() {
  window.location.href = "/frontend/progress.html";
}

// ============================================================
// LOGOUT
// ============================================================
function logout() {
  localStorage.clear();
  window.location.href = "/frontend/index.html";
}

// ============================================================
// START
// ============================================================
loadBooks();