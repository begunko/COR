// static/js/portal.js
// ==============================================================================
// ПОРТАЛ — страница входа
// ==============================================================================

const API = '/api/v1/auth/login/';

function showError(text) {
    const el = document.getElementById('error');
    el.textContent = text;
    el.style.display = 'block';
}

function hideError() {
    document.getElementById('error').style.display = 'none';
}

async function login() {
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;

    if (!email || !password) {
        showError('Введи email и пароль');
        return;
    }

    hideError();

    try {
        const response = await fetch(API, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (response.ok && data.access) {
            localStorage.setItem('cor_token', data.access);
            window.location.href = '/editor/';
        } else {
            showError(data.detail || 'Неверный email или пароль');
        }
    } catch (e) {
        console.error('Ошибка:', e);
        showError('Сервер не отвечает. Проверь, запущен ли сервер.');
    }
}

// ===== ОБРАБОТЧИКИ =====
document.getElementById('login-btn').addEventListener('click', login);

document.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') login();
});

document.getElementById('guest-btn').addEventListener('click', () => {
    window.location.href = '/editor/';
});

// Авто-вход
if (localStorage.getItem('cor_token')) {
    window.location.href = '/editor/';
}