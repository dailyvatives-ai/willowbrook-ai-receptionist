const gate = document.getElementById('gate');
const dashboard = document.getElementById('dashboard');
const adminKeyInput = document.getElementById('adminKeyInput');
const unlockBtn = document.getElementById('unlockBtn');
const gateError = document.getElementById('gateError');
const refreshBtn = document.getElementById('refreshBtn');
const leadsList = document.getElementById('leadsList');
const leadsEmpty = document.getElementById('leadsEmpty');

let adminKey = sessionStorage.getItem('willowbrook_admin_key') || '';

function urgencyLabel(u) {
  return { routine: 'Routine', urgent: 'Urgent', emergency: 'Emergency' }[u] || u;
}

function formatTime(ts) {
  const d = new Date(ts * 1000);
  return d.toLocaleString();
}

function renderLeads(leads) {
  leadsList.innerHTML = '';
  if (!leads.length) {
    leadsEmpty.classList.remove('hidden');
    return;
  }
  leadsEmpty.classList.add('hidden');

  leads.forEach((lead) => {
    const card = document.createElement('div');
    card.className = 'lead-card';
    card.innerHTML = `
      <span class="lead-urgency ${lead.urgency}">${urgencyLabel(lead.urgency)}</span>
      <div class="lead-main">
        <strong>${escapeHtml(lead.name || 'Unknown')}</strong>
        <p>${escapeHtml(lead.reason || '')} — prefers ${escapeHtml(lead.preferred_time || 'no time given')}${lead.phone ? ' · ' + escapeHtml(lead.phone) : ''}</p>
      </div>
      <span class="lead-time">${formatTime(lead.captured_at)}</span>
    `;
    leadsList.appendChild(card);
  });
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

async function fetchLeads() {
  const res = await fetch('/api/admin/leads', {
    headers: { 'x-admin-key': adminKey },
  });
  if (res.status === 401) {
    throw new Error('unauthorized');
  }
  return res.json();
}

async function unlock() {
  adminKey = adminKeyInput.value.trim();
  gateError.textContent = '';
  try {
    const leads = await fetchLeads();
    sessionStorage.setItem('willowbrook_admin_key', adminKey);
    gate.classList.add('hidden');
    dashboard.classList.remove('hidden');
    renderLeads(leads);
  } catch (err) {
    gateError.textContent = 'Incorrect key — please try again.';
  }
}

unlockBtn.addEventListener('click', unlock);
adminKeyInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') unlock();
});

refreshBtn.addEventListener('click', async () => {
  try {
    const leads = await fetchLeads();
    renderLeads(leads);
  } catch (err) {
    // key may have expired/changed — send back to gate
    dashboard.classList.add('hidden');
    gate.classList.remove('hidden');
  }
});

// auto-unlock if we already have a stored key
if (adminKey) {
  adminKeyInput.value = adminKey;
  unlock();
}
