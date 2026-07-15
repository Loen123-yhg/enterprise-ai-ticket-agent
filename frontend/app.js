const API_BASE = "http://127.0.0.1:8000";

window.onload = function () {
  loadTickets();
};

function showMessage(text) {
  document.getElementById("message").textContent = text || "";
}

async function requestJson(url, options = {}) {
  const response = await fetch(url, options);

  if (!response.ok) {
    let errorText = `请求失败：${response.status}`;

    try {
      const errorData = await response.json();
      if (errorData.detail) {
        errorText = typeof errorData.detail === "string"
          ? errorData.detail
          : JSON.stringify(errorData.detail);
      }
    } catch {
      errorText = response.statusText;
    }

    throw new Error(errorText);
  }

  return response.json();
}

async function createTicket() {
  const userName = document.getElementById("userName").value.trim();
  const question = document.getElementById("question").value.trim();
  const priority = document.getElementById("priority").value;

  if (!userName || !question) {
    showMessage("用户名和问题描述不能为空");
    return;
  }

  try {
    showMessage("");

    await requestJson(`${API_BASE}/tickets`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        user_name: userName,
        question: question,
        priority: priority
      })
    });

    document.getElementById("userName").value = "";
    document.getElementById("question").value = "";
    document.getElementById("priority").value = "low";

    await loadTickets();
  } catch (error) {
    showMessage(error.message);
  }
}

async function loadTickets() {
  try {
    showMessage("");

    const tickets = await requestJson(`${API_BASE}/tickets`);
    renderTickets(tickets);
  } catch (error) {
    showMessage(error.message);
  }
}

async function searchTickets() {
  const keyword = document.getElementById("searchKeyword").value.trim();
  const priority = document.getElementById("searchPriority").value;
  const status = document.getElementById("searchStatus").value;

  const params = new URLSearchParams();

  if (keyword) {
    params.append("q", keyword);
  }

  if (priority) {
    params.append("priority", priority);
  }

  if (status) {
    params.append("status", status);
  }

  try {
    showMessage("");

    const url = `${API_BASE}/tickets/search?${params.toString()}`;
    const tickets = await requestJson(url);
    renderTickets(tickets);
  } catch (error) {
    showMessage(error.message);
  }
}

async function updateTicketStatus(ticketId) {
  const statusSelect = document.getElementById(`status-${ticketId}`);
  const newStatus = statusSelect.value;

  try {
    showMessage("");

    await requestJson(`${API_BASE}/tickets/${ticketId}`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        status: newStatus
      })
    });

    await loadTickets();
  } catch (error) {
    showMessage(error.message);
  }
}

async function analyzeTicket(ticketId) {
  const resultBox = document.getElementById(`ai-${ticketId}`);
  resultBox.textContent = "AI 分析中...";

  try {
    showMessage("");

    const data = await requestJson(`${API_BASE}/tickets/${ticketId}/ai-analysis`, {
      method: "POST"
    });

    resultBox.textContent = data.ai_analysis;
  } catch (error) {
    resultBox.textContent = "";
    showMessage(error.message);
  }
}

function renderTickets(tickets) {
  const container = document.getElementById("tickets");
  const count = document.getElementById("ticketCount");

  count.textContent = `${tickets.length} 条`;
  container.innerHTML = "";

  if (tickets.length === 0) {
    container.innerHTML = `<p class="ticket-meta">暂无工单</p>`;
    return;
  }

  tickets.forEach((ticket) => {
    const card = document.createElement("div");
    card.className = "ticket-card";

    card.innerHTML = `
      <div class="ticket-top">
        <div>
          <div class="ticket-title">#${ticket.id} ${escapeHtml(ticket.user_name)}</div>
          <div class="ticket-meta">
            优先级：<span class="badge">${ticket.priority}</span>
            状态：<span class="badge">${ticket.status}</span>
          </div>
        </div>
      </div>

      <div class="ticket-question">${escapeHtml(ticket.question)}</div>

      <div class="ticket-actions">
        <select id="status-${ticket.id}">
          <option value="open" ${ticket.status === "open" ? "selected" : ""}>open</option>
          <option value="in_progress" ${ticket.status === "in_progress" ? "selected" : ""}>in_progress</option>
          <option value="closed" ${ticket.status === "closed" ? "selected" : ""}>closed</option>
        </select>

        <button onclick="updateTicketStatus(${ticket.id})">更新状态</button>
        <button class="secondary" onclick="analyzeTicket(${ticket.id})">AI 分析</button>
      </div>

      <div id="ai-${ticket.id}" class="ai-result"></div>
    `;

    container.appendChild(card);
  });
}

function escapeHtml(text) {
  return String(text)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
