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
// If no token found, send back to login
// ============================================================
if (!token) {
  window.location.href = "index.html";
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
    math:        "📐",
    science:     "🔬",
    english:     "📖",
    history:     "🏛️",
    geography:   "🌍",
    computer:    "💻",
    hindi:       "📝",
    marathi:     "📝",
    social:      "🌐",
    default:     "📚"
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
  

  // When student clicks the card
  card.onclick = () => {
    // Save selected book info to localStorage
    localStorage.setItem("selected_book_id",      book.id);
    localStorage.setItem("selected_book_subject",  book.subject);
    localStorage.setItem("selected_book_title",    book.title);

    // Go to chat page
    window.location.href = "chat.html";
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
      headers: {
        "Authorization": `Bearer ${token}`
      }
    });

    const books = await response.json();

    // Hide loading state
    document.getElementById("loading-state").classList.add("hidden");

    if (!response.ok) {
      // Token expired or other error — go back to login
      window.location.href = "index.html";
      return;
    }

    if (books.length === 0) {
      // No books found — show empty state
      document.getElementById("empty-state").classList.remove("hidden");
      return;
    }

    // Add each book card to the grid
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
// CONCEPT 7 — Logout
// ============================================================
function logout() {
  localStorage.clear();
  window.location.href = "index.html";
}

// ============================================================
// START — Run loadBooks when page opens
// ============================================================
loadBooks();