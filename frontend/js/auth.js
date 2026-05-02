const API = "http://127.0.0.1:8000";

// ============================================================
// JOB 1 — TAB SWITCHER
// ============================================================
function showTab(tab) {
  document.getElementById("login-tab").classList.add("hidden");
  document.getElementById("register-tab").classList.add("hidden");

  document.querySelectorAll(".tab-btn").forEach(btn => {
    btn.classList.remove("active");
  });

  document.getElementById(tab + "-tab").classList.remove("hidden");

  const buttons = document.querySelectorAll(".tab-btn");
  if (tab === "login")    buttons[0].classList.add("active");
  if (tab === "register") buttons[1].classList.add("active");
}

// ============================================================
// HELPER — SHOW MESSAGE
// ============================================================
function showMsg(id, text, type) {
  const el = document.getElementById(id);
  el.textContent = text;
  el.className = "msg " + type;
}

// ============================================================
// JOB 2 — LOGIN
// ============================================================
async function loginUser() {
  const email    = document.getElementById("login-email").value.trim();
  const password = document.getElementById("login-password").value;

  if (!email || !password) {
    showMsg("login-msg", "Please fill in all fields.", "error");
    return;
  }

  // ❌ DELETE these 3 lines (FormData) — already removed
  // ✅ directly use fetch with JSON below

  try {
    const response = await fetch(`${API}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: email, password: password })
    });

    const data = await response.json();
    console.log(data);   // temporary debug line

    if (!response.ok) {
      showMsg("login-msg", data.detail || "Login failed.", "error");
      return;
    }

    localStorage.setItem("token", data.access_token);
    localStorage.setItem("role",  data.role);
    localStorage.setItem("grade", data.grade);
    localStorage.setItem("name",  data.name);

    showMsg("login-msg", "Login successful! Redirecting...", "success");

    setTimeout(() => {
      if (data.role === "admin") {
        window.location.href = "admin.html";
      } else {
        window.location.href = "dashboard.html";
      }
    }, 1000);

  } catch (err) {
    showMsg("login-msg", "Cannot connect to server. Is FastAPI running?", "error");
  }
}

// ============================================================
// JOB 3 — REGISTER
// ============================================================
async function registerUser() {
  const name     = document.getElementById("reg-name").value.trim();
  const email    = document.getElementById("reg-email").value.trim();
  const password = document.getElementById("reg-password").value;
  const grade    = document.getElementById("reg-grade").value;
  const role     = document.getElementById("reg-role").value;
  const lang     = document.getElementById("reg-lang").value;

  if (!name || !email || !password) {
    showMsg("reg-msg", "Name, email and password are required.", "error");
    return;
  }

  const body = {
    name:           name,
    email:          email,
    password:       password,
    role:           role,
    preferred_lang: lang,
    grade:          grade ? parseInt(grade) : null
  };

  try {
    const response = await fetch(`${API}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });

    const data = await response.json();

    if (!response.ok) {
      showMsg("reg-msg", data.detail || "Registration failed.", "error");
      return;
    }

    showMsg("reg-msg", "Account created! Please login now.", "success");
    setTimeout(() => showTab("login"), 1500);

  } catch (err) {
    showMsg("reg-msg", "Cannot connect to server. Is FastAPI running?", "error");
  }
}