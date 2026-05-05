// ============================================================
// progress.js — Student Progress Page
// ============================================================

const API   = "http://127.0.0.1:8000";
const token = localStorage.getItem("token");
const name  = localStorage.getItem("name");

// ============================================================
// PROTECT PAGE
// ============================================================
if (!token || token === "null" || token === "undefined") {
  window.location.href = "/frontend/index.html";
}

// ============================================================
// FILL PAGE INFO
// ============================================================
document.getElementById("user-greeting").textContent = `Welcome, ${name}!`;

// ============================================================
// LOAD PROGRESS
// ============================================================
async function loadProgress() {
  try {
    const res  = await fetch(`${API}/progress/my`, {
      headers: { "Authorization": `Bearer ${token}` }
    });

    const data = await res.json();
    document.getElementById("progress-loading").classList.add("hidden");

    if (!res.ok) {
      document.getElementById("progress-empty").classList.remove("hidden");
      return;
    }

    const progress = data.progress || [];

    if (progress.length === 0) {
      document.getElementById("progress-empty").classList.remove("hidden");
      return;
    }

    // Fill summary cards
    const totalSubjects = progress.length;
    const avgScore      = (
      progress.reduce((sum, p) => sum + p.understanding_score, 0) / totalSubjects
    ).toFixed(1);
    const totalDoubts   = progress.reduce((sum, p) => sum + p.doubt_count, 0);

    document.getElementById("stat-subjects").textContent  = totalSubjects;
    document.getElementById("stat-avg-score").textContent = avgScore + "/10";
    document.getElementById("stat-doubts").textContent    = totalDoubts;

    // Render progress cards
    const grid = document.getElementById("progress-grid");
    grid.innerHTML = "";

    progress.forEach(p => {
      const card = createProgressCard(p);
      grid.appendChild(card);
    });

  } catch (err) {
    document.getElementById("progress-loading").textContent =
      "Cannot connect to server.";
  }
}

// ============================================================
// CREATE PROGRESS CARD
// ============================================================
function createProgressCard(p) {
  const card = document.createElement("div");
  card.className = "progress-card";

  // Score color
  const score     = p.understanding_score || 0;
  const scoreColor = score >= 7 ? "#22c55e" : score >= 4 ? "#f59e0b" : "#ef4444";
  const scoreLabel = score >= 7 ? "Great!" : score >= 4 ? "Keep Going!" : "Needs Revision";
  const barWidth   = (score / 10 * 100).toFixed(0);

  // Weak areas
  const weakAreas = p.weak_areas
    ? p.weak_areas.split(",").map(w => w.trim()).filter(w => w)
    : [];

  // Suggested revision
  const suggestions = p.suggested_revision
    ? p.suggested_revision.split(",").map(s => s.trim()).filter(s => s)
    : [];

  // Last studied
  const lastStudied = p.last_studied
    ? new Date(p.last_studied).toLocaleDateString("en-IN", {
        day: "numeric", month: "short", year: "numeric"
      })
    : "Not yet";

  card.innerHTML = `
    <div class="progress-card-header">
      <div class="progress-subject">${p.subject}</div>
      <div class="progress-score-badge" style="background: ${scoreColor}20; color: ${scoreColor};">
        ${scoreLabel}
      </div>
    </div>

    <div class="progress-score-row">
      <span class="progress-score-label">Understanding</span>
      <span class="progress-score-value" style="color: ${scoreColor}">
        ${score.toFixed(1)}/10
      </span>
    </div>

    <div class="progress-bar-bg">
      <div class="progress-bar-fill" style="width: ${barWidth}%; background: ${scoreColor};"></div>
    </div>

    <div class="progress-meta">
      <span>🤔 Doubts: ${p.doubt_count}</span>
      <span>📅 Last studied: ${lastStudied}</span>
    </div>

    ${weakAreas.length ? `
    <div class="progress-section">
      <div class="progress-section-title">🔴 Weak Topics</div>
      <div class="progress-tags">
        ${weakAreas.map(w => `<span class="tag tag-weak">${w}</span>`).join("")}
      </div>
    </div>` : ""}

    ${suggestions.length ? `
    <div class="progress-section">
      <div class="progress-section-title">🔄 Suggested Revision</div>
      <div class="progress-tags">
        ${suggestions.map(s => `<span class="tag tag-suggest">${s}</span>`).join("")}
      </div>
    </div>` : ""}
  `;

  return card;
}

// ============================================================
// NAVIGATION
// ============================================================
function goBack() {
  window.location.href = "/frontend/dashboard.html";
}

function logout() {
  localStorage.clear();
  window.location.href = "/frontend/index.html";
}

// ============================================================
// START
// ============================================================
loadProgress();