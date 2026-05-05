// ============================================================
// admin.js — Admin Dashboard
// ============================================================

const API = "http://127.0.0.1:8000";

// ============================================================
// READ FROM LOCALSTORAGE
// ============================================================
const token = localStorage.getItem("token");
const role  = localStorage.getItem("role");
const name  = localStorage.getItem("name");

// ============================================================
// PROTECT PAGE — admin only
// ============================================================
if (!token || role !== "admin") {
  window.location.href = "/frontend/index.html";
}

// ============================================================
// FILL PAGE INFO
// ============================================================
document.getElementById("user-greeting").textContent = `Welcome, ${name}!`;

// ============================================================
// LOAD STATS
// ============================================================
async function loadStats() {
  try {
    const res  = await fetch(`${API}/admin/stats`, {
      headers: { "Authorization": `Bearer ${token}` }
    });
    const data = await res.json();

    document.getElementById("stat-books").textContent    = data.total_books;
    document.getElementById("stat-students").textContent = data.total_students;
    document.getElementById("stat-chats").textContent    = data.total_chats;

  } catch (err) {
    console.error("Stats error:", err);
  }
}

// ============================================================
// LOAD ALL BOOKS
// ============================================================
async function loadBooks() {
  try {
    const res   = await fetch(`${API}/admin/books`, {
      headers: { "Authorization": `Bearer ${token}` }
    });
    const books = await res.json();

    document.getElementById("books-loading").classList.add("hidden");

    if (!books.length) {
      document.getElementById("books-empty").classList.remove("hidden");
      document.getElementById("books-table").classList.add("hidden");
      return;
    }

    document.getElementById("books-table").classList.remove("hidden");
    const tbody = document.getElementById("books-tbody");
    tbody.innerHTML = "";

    books.forEach((book, idx) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${idx + 1}</td>
        <td>${book.title}</td>
        <td>${book.subject}</td>
        <td>Grade ${book.grade}</td>
        <td>${book.uploaded_at}</td>
        <td>
          <button class="btn-delete" onclick="deleteBook(${book.id}, '${book.title}')">
            🗑️ Delete
          </button>
        </td>
      `;
      tbody.appendChild(tr);
    });

  } catch (err) {
    document.getElementById("books-loading").textContent = "Could not load books.";
  }
}

// ============================================================
// LOAD ALL STUDENTS
// ============================================================
async function loadStudents() {
  try {
    const res      = await fetch(`${API}/admin/students`, {
      headers: { "Authorization": `Bearer ${token}` }
    });
    const students = await res.json();

    document.getElementById("students-loading").classList.add("hidden");

    if (!students.length) {
      document.getElementById("students-empty").classList.remove("hidden");
      document.getElementById("students-table").classList.add("hidden");
      return;
    }

    document.getElementById("students-table").classList.remove("hidden");
    const tbody = document.getElementById("students-tbody");
    tbody.innerHTML = "";

    students.forEach((s, idx) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${idx + 1}</td>
        <td>${s.name}</td>
        <td>${s.email}</td>
        <td>Grade ${s.grade}</td>
        <td>${s.preferred_lang}</td>
      `;
      tbody.appendChild(tr);
    });

  } catch (err) {
    document.getElementById("students-loading").textContent = "Could not load students.";
  }
}

// ============================================================
// UPLOAD BOOK
// ============================================================
async function uploadBook() {
  const title   = document.getElementById("book-title").value.trim();
  const subject = document.getElementById("book-subject").value.trim();
  const grade   = document.getElementById("book-grade").value;
  const file    = document.getElementById("book-file").files[0];

  // Validate
  if (!title || !subject || !grade || !file) {
    showUploadMsg("Please fill in all fields and select a PDF.", "error");
    return;
  }

  if (!file.name.endsWith(".pdf")) {
    showUploadMsg("Only PDF files are allowed.", "error");
    return;
  }

  // Build FormData
  const formData = new FormData();
  formData.append("title",   title);
  formData.append("subject", subject);
  formData.append("grade",   grade);
  formData.append("file",    file);

  // Disable button during upload
  const btn = document.getElementById("upload-btn");
  btn.disabled     = true;
  btn.textContent  = "⏳ Uploading...";

  showUploadMsg("Uploading and processing PDF — this may take a moment...", "info");

  try {
    const res  = await fetch(`${API}/books/upload`, {
      method:  "POST",
      headers: { "Authorization": `Bearer ${token}` },
      body:    formData
    });
    const data = await res.json();

    if (!res.ok) {
      showUploadMsg(data.detail || "Upload failed.", "error");
      return;
    }

    showUploadMsg(`✅ "${data.title}" uploaded successfully!`, "success");

    // Clear form
    document.getElementById("book-title").value   = "";
    document.getElementById("book-subject").value = "";
    document.getElementById("book-grade").value   = "";
    document.getElementById("book-file").value    = "";

    // Refresh books list and stats
    await loadBooks();
    await loadStats();

  } catch (err) {
    showUploadMsg("Cannot connect to server.", "error");
  } finally {
    btn.disabled    = false;
    btn.textContent = "📤 Upload Book";
  }
}

// ============================================================
// DELETE BOOK
// ============================================================
async function deleteBook(bookId, bookTitle) {
  const confirmed = confirm(`Are you sure you want to delete "${bookTitle}"?`);
  if (!confirmed) return;

  try {
    const res = await fetch(`${API}/admin/books/${bookId}`, {
      method:  "DELETE",
      headers: { "Authorization": `Bearer ${token}` }
    });

    if (!res.ok) {
      const data = await res.json();
      alert(data.detail || "Delete failed.");
      return;
    }

    // Refresh books list and stats
    await loadBooks();
    await loadStats();

  } catch (err) {
    alert("Cannot connect to server.");
  }
}

// ============================================================
// HELPER — Show upload message
// ============================================================
function showUploadMsg(text, type) {
  const el = document.getElementById("upload-msg");
  el.textContent = text;
  el.className   = "msg " + type;
}

// ============================================================
// LOGOUT
// ============================================================
function logout() {
  localStorage.clear();
  window.location.href = "/frontend/index.html";
}

// ============================================================
// START — load everything on page open
// ============================================================
loadStats();
loadBooks();
loadStudents();