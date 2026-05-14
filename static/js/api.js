const API_BASE = '/api/v1';

async function apiFetch(path, options = {}) {
    const token = localStorage.getItem('token');
    const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const res = await fetch(API_BASE + path, { ...options, headers });

    if (res.status === 401) {
        localStorage.clear();
        window.location.href = '/login';
        return;
    }
    if (res.status === 204) return null;
    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(err.detail || res.statusText);
    }
    return res.json();
}

function requireAuth() {
    if (!localStorage.getItem('token')) {
        window.location.href = '/login';
    }
}

function getUser() {
    try { return JSON.parse(localStorage.getItem('user')); } catch { return null; }
}

function logout() {
    localStorage.clear();
    window.location.href = '/login';
}

function showError(elementId, message) {
    const el = document.getElementById(elementId);
    if (el) { el.textContent = message; el.classList.remove('d-none'); }
}

function hideError(elementId) {
    const el = document.getElementById(elementId);
    if (el) el.classList.add('d-none');
}

function statusBadge(status) {
    const map = { todo: 'secondary', in_progress: 'primary', done: 'success' };
    const label = { todo: 'To Do', in_progress: 'In Progress', done: 'Done' };
    return `<span class="badge bg-${map[status] || 'secondary'}">${label[status] || status}</span>`;
}

function priorityBadge(priority) {
    const map = { low: 'info', medium: 'warning', high: 'danger' };
    return `<span class="badge bg-${map[priority] || 'secondary'}">${priority}</span>`;
}
