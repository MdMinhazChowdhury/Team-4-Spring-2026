const API_BASE = window.FINTRAC_API_BASE || "http://127.0.0.1:5000";
let currentUserId = Number(localStorage.getItem("fintrac_user_id")) || 1;
let calendarInstance = null;

function money(value) {
  const n = Number(value || 0);
  return "$" + n.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function statusMessage(message, isError = false) {
  const box = document.getElementById("app-status") || document.getElementById("login-status");
  if (!box) return;
  box.textContent = message;
  box.style.display = "block";
  box.style.background = isError ? "#7f1d1d" : "#111";
}

async function api(path, options = {}) {
  const opts = { ...options };
  opts.headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  const response = await fetch(API_BASE + path, opts);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.error || data.message || `HTTP ${response.status}`);
  }
  return data;
}

function showTab(tabID) {
  const tab = document.getElementById(tabID);
  if (!tab) throw new Error("Tab not found: " + tabID);
  document.querySelectorAll(".tab-content").forEach(t => t.classList.remove("active"));
  document.querySelectorAll(".nav-link").forEach(btn => btn.classList.remove("active"));
  tab.classList.add("active");
  const matchingButton = Array.from(document.querySelectorAll(".nav-link"))
    .find(btn => (btn.getAttribute("onclick") || "").includes(tabID));
  if (matchingButton) matchingButton.classList.add("active");
}

function transactionHtml(t) {
  const sign = t.tx_type === "income" ? "+" : "-";
  return `<div class="transaction-list rec-transaction">
    <div class="tran-left"><div class="top"><p class="name">${t.description || t.category}</p></div>
    <div class="bottom"><p class="type">${t.category}</p><p class="date">${t.date}</p></div></div>
    <div class="tran-right"><p class="dollar">${sign}${money(t.amount)}</p></div>
  </div>`;
}

async function loadDashboard() {
  const d = await api(`/dashboard/${currentUserId}`);
  document.querySelector(".total-balance .number").textContent = money(d.total_balance);
  document.querySelector(".monthly-income .number").textContent = money(d.monthly_income);
  document.querySelector(".monthly-expenses .number").textContent = money(d.monthly_expenses);
  document.querySelector(".net-savings .number").textContent = money(d.net_savings);

  const recent = document.querySelector(".recent-transaction");
  if (recent) {
    const controls = recent.querySelectorAll(":scope > .rec-title, :scope > .filter-link");
    recent.innerHTML = "";
    controls.forEach(c => recent.appendChild(c));
    recent.insertAdjacentHTML("beforeend", (d.recent_transactions || []).map(transactionHtml).join("") || "<p>No transactions yet.</p>");
  }

  const chart = document.querySelector(".pie-chart");
  if (chart) {
    const rows = Object.entries(d.spending_by_category || {}).map(([k, v]) => `${k}: ${v}%`).join("<br>");
    chart.innerHTML = rows || "No expense data";
  }
}

async function loadTransactions(filter = "all") {
  const txs = await api(`/transactions/${currentUserId}?filter=${filter}`);
  const list = document.getElementById("transaction-history-list") || document.querySelector(".transaction-history");
  if (!list) return;
  list.innerHTML = txs.map(transactionHtml).join("") || "<p>No transactions match this filter.</p>";
}

async function loadSubscriptions() {
  const data = await api(`/subscriptions/${currentUserId}`);
  document.querySelector(".total-sub .number").textContent = data.total_count;
  document.querySelector(".monthly-cost .number").textContent = money(data.monthly_cost);
  document.querySelector(".renew .number").textContent = (data.renewing_this_week || []).length;
  const container = document.querySelector(".active-sub");
  if (container) {
    container.innerHTML = `<p class="title">Active Subscription</p>` + (data.subscriptions || []).map(s =>
      `<div class="act-sub"><div class="act-left"><p class="name">${s.title}</p><p class="date">${s.renewal_display}</p></div><div class="act-right"><p class="days">${s.days_until_renewal} days</p><p class="dollar">${money(s.cost)}/mo</p></div></div>`
    ).join("") || `<p class="title">Active Subscription</p><p>No subscriptions yet.</p>`;
  }
}

async function loadSavingsGoals() {
  const goals = await api(`/savings-goals/${currentUserId}`);
  const cards = document.querySelector("#savings-goals-area .topcards");
  if (cards) {
    cards.innerHTML = goals.map((g, idx) => `<div class="goal"><p class="title">${g.goal_name}</p><p class="number">${money(g.current_amount)} / ${money(g.target_amount)}</p><progress id="progress-bar${idx+1}" class="progress-bar" value="${g.progress_percent}" max="100"></progress><p>${g.due_display}</p></div>`).join("") || "<p>No savings goals yet.</p>";
  }
  const dashGoals = document.querySelector(".dash-right .savings-goals");
  if (dashGoals) {
    dashGoals.innerHTML = `<p class="title">Savings Goals</p>` + goals.slice(0, 3).map((g, idx) => `<div class="save-goal"><p class="name">${g.goal_name}</p><progress id="dash-progress-${idx}" class="progress-bar" value="${g.progress_percent}" max="100"></progress></div>`).join("");
  }
}

async function loadCalendar() {
  const data = await api(`/calendar/${currentUserId}`);
  const renewals = document.querySelector(".cal-right");
  if (renewals) {
    renewals.innerHTML = `<p class="title">Upcoming Renewals</p>` + (data.events || []).map(e => `<div class="sub-renew"><div class="sub-left"><p class="name">${e.title}</p><p class="date">${e.date}</p></div><div class="sub-right"><p class="dollar">${money(e.cost)}</p></div></div>`).join("") || `<p class="title">Upcoming Renewals</p><p>No upcoming renewals.</p>`;
  }
  const calendarEl = document.getElementById("calendar");
  if (calendarEl && window.FullCalendar) {
    if (calendarInstance) calendarInstance.destroy();
    calendarInstance = new FullCalendar.Calendar(calendarEl, {
      initialView: "dayGridMonth",
      events: (data.events || []).map(e => ({ title: `${e.title} ${money(e.cost)}`, start: e.date }))
    });
    calendarInstance.render();
  } else if (calendarEl) {
    calendarEl.innerHTML = `<div style="padding:16px"><strong>Renewal Calendar</strong><br>` +
      ((data.events || []).map(e => `${e.date}: ${e.title} ${money(e.cost)}`).join("<br>") || "No renewals") +
      `</div>`;
  }
}

async function refreshAll() {
  if (!document.getElementById("dashboard-area")) return;
  await Promise.allSettled([loadDashboard(), loadTransactions(), loadSubscriptions(), loadSavingsGoals(), loadCalendar()]);
}

function wireMainPage() {
  showTab("dashboard-area");
  document.getElementById("transaction-submit")?.addEventListener("click", async () => {
    try {
      const category = document.getElementById("transaction-category").value;
      await api("/transactions", { method: "POST", body: JSON.stringify({
        user_id: currentUserId,
        amount: Number(document.getElementById("transaction-amount").value),
        date: document.getElementById("transaction-date").value,
        description: document.getElementById("transaction-description").value.trim(),
        category,
        tx_type: category === "Income" ? "income" : "expense"
      })});
      statusMessage("Transaction saved and dashboard refreshed.");
      await refreshAll();
    } catch (e) { statusMessage(e.message, true); }
  });
  document.getElementById("transaction-cancel")?.addEventListener("click", () => {
    ["transaction-amount", "transaction-date", "transaction-description"].forEach(id => document.getElementById(id).value = "");
  });
  document.querySelectorAll(".transaction-history .filter-link").forEach(btn => btn.addEventListener("click", () => {
    const label = btn.textContent.trim().toLowerCase().replaceAll(" ", "_");
    loadTransactions(label === "all" ? "all" : label);
  }));
  document.getElementById("goal-submit")?.addEventListener("click", async () => {
    try {
      await api("/savings-goals", { method: "POST", body: JSON.stringify({
        user_id: currentUserId,
        goal_name: document.getElementById("goal-name").value.trim(),
        current_amount: Number(document.getElementById("goal-current").value || 0),
        target_amount: Number(document.getElementById("goal-target").value),
        deadline: document.getElementById("goal-deadline").value || null
      })});
      statusMessage("Savings goal saved and displayed.");
      await refreshAll();
    } catch (e) { statusMessage(e.message, true); }
  });
  document.querySelector(".gen-report")?.addEventListener("click", async () => {
    try {
      const report = await api(`/report/${currentUserId}`);
      statusMessage(`Report ${report.report_month}: Income ${money(report.total_income)}, Expenses ${money(report.total_expenses)}, Net ${money(report.net_savings)}`);
    } catch (e) { statusMessage(e.message, true); }
  });
  refreshAll().catch(e => statusMessage("Backend unavailable: start Flask on port 5000.", true));
}

function wireLoginPage() {
  const form = document.getElementById("login-form");
  if (!form) return;
  form.addEventListener("submit", async (ev) => {
    ev.preventDefault();
    const username = document.getElementById("login-username").value.trim();
    const password = document.getElementById("login-password").value;
    const email = username.includes("@") ? username : `${username}@fintrac.local`;
    try {
      let data;
      try {
        data = await api("/login", { method: "POST", body: JSON.stringify({ email, password }) });
      } catch (_) {
        data = await api("/register", { method: "POST", body: JSON.stringify({ username, email, password }) });
      }
      localStorage.setItem("fintrac_user_id", data.user_id || 1);
      localStorage.setItem("fintrac_username", data.username || username);
      statusMessage("Login/register successful. Opening dashboard...");
      window.location.href = "mainpage.html";
    } catch (e) { statusMessage(e.message, true); }
  });
  document.getElementById("google-login")?.addEventListener("click", async () => {
    try {
      const data = await api("/google-login", { method: "POST", body: JSON.stringify({ username: "Demo User", email: "demo@fintrac.local" }) });
      localStorage.setItem("fintrac_user_id", data.user_id || 1);
      window.location.href = "mainpage.html";
    } catch (e) { statusMessage(e.message, true); }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  if (document.getElementById("dashboard-area")) wireMainPage();
  if (document.getElementById("login-form")) wireLoginPage();
});
