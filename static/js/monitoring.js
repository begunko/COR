/**
 * ================================================================
 * COR ENGINE — Monitoring Dashboard Logic
 * ================================================================
 */

'use strict';

const state = {
    tab: 'overview',
    errorTab: 'all',
};

document.addEventListener('DOMContentLoaded', () => {
    console.log('💻 COR Monitoring Dashboard v2.0');

    // Сразу показываем таб Обзор
    showTab('overview');

    // Вешаем обработчики
    initToolbarTabs();
    initErrorTabs();

    // Загружаем данные
    loadAllData();
    setInterval(loadAllData, 5000);
});

// ==============================
// ТУЛБАР: КНОПКИ ТАБОВ
// ==============================
function initToolbarTabs() {
    document.querySelectorAll('#cor-topbar .cor-topbar-link[data-tab]').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('#cor-topbar .cor-topbar-link[data-tab]').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            state.tab = btn.dataset.tab;
            showTab(state.tab);
        });
    });
}

function showTab(tabName) {
    document.querySelectorAll('.monitoring-tab').forEach(tab => {
        tab.style.display = 'none';
    });
    const tab = document.getElementById(`tab-${tabName}`);
    if (tab) {
        tab.style.display = 'block';
    }
}

// ==============================
// ПОД-ТАБЫ ОШИБОК
// ==============================
function initErrorTabs() {
    document.querySelectorAll('.monitoring-error-tab[data-error-tab]').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.monitoring-error-tab[data-error-tab]').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            state.errorTab = tab.dataset.errorTab;
            filterErrors(state.errorTab);
        });
    });
}

function filterErrors(type) {
    document.querySelectorAll('#error-list .error-item').forEach(item => {
        if (type === 'all') {
            item.style.display = 'block';
        } else {
            item.style.display = item.classList.contains(`error-${type}`) ? 'block' : 'none';
        }
    });
}

// ==============================
// ЗАГРУЗКА ДАННЫХ
// ==============================
async function loadAllData() {
    try {
        const response = await fetch('/api/monitoring/');
        if (!response.ok) throw new Error('API недоступен');
        const data = await response.json();
        updateAllTabs(data);
    } catch (err) {
        console.warn('⚠️ API мониторинга:', err.message);
    }
}

function updateAllTabs(data) {
    updateOverview(data);
    updateErrors(data);
    updateChunks(data);
    updateUsers(data);
    updateDatabase(data);
}

function updateOverview(data) {
    setText('stat-server-status', '🟢 Online');
    setText('stat-uptime', data.uptime || '—');

    const cpu = data.cpu_percent || 0;
    setText('stat-cpu', cpu + '%');
    updateBar('stat-cpu-bar', cpu);

    const ramPct = data.ram_percent || 0;
    setText('stat-ram', (data.ram_used || '?') + ' / ' + (data.ram_total || '?'));
    updateBar('stat-ram-bar', ramPct);

    const diskPct = data.disk_percent || 0;
    setText('stat-disk', (data.disk_used || '?') + ' / ' + (data.disk_total || '?'));
    updateBar('stat-disk-bar', diskPct);

    setText('stat-chunks', (data.chunks_active || 0) + ' / ' + (data.chunks_total || 0));
    setText('stat-chunks-loaded', data.chunks_loaded || 0);
    setText('stat-users-online', data.users_online || 0);
    setText('stat-users-today', data.users_today || 0);
    setText('stat-objects', data.objects_total || 0);
    setText('stat-assets', data.assets_active || data.assets_total || 0);

    const totalRecords = (data.objects_total || 0) + (data.chunks_total || 0) +
        (data.assets_total || 0) + (data.tools_active || 0) +
        (data.users_total || 0);
    setText('stat-db-total', totalRecords);
}

function updateErrors(data) {
    const errors = data.errors || [];
    const container = document.getElementById('error-list');
    if (!container) return;

    if (errors.length === 0 || (errors.length === 1 && errors[0].message?.includes('Ошибок не обнаружено'))) {
        container.innerHTML = `<div class="error-item error-system">
            <div class="error-header"><span class="error-type">🟢 СИСТЕМА</span><span class="error-time">—</span></div>
            <div class="error-message">Ошибок не обнаружено</div></div>`;
        return;
    }

    container.innerHTML = errors.map(e => {
        // Определяем тип ошибки для CSS-класса и иконки
        let errorClass = 'error-server'; // По умолчанию красный (серверная ошибка)
        let typeLabel = '🔴 СЕРВЕР';

        if (e.type === 'warning' || e.type === 'chunk') {
            errorClass = 'error-chunk';
            typeLabel = '🟠 ЧАНК';
        } else if (e.type === 'browser' || e.type === 'client') {
            errorClass = 'error-browser';
            typeLabel = '🟡 БРАУЗЕР';
        } else if (e.type === 'system' || e.type === 'server') {
            // Системные сообщения без ошибок
            errorClass = 'error-system';
            typeLabel = '🟢 СИСТЕМА';
        }

        // Используем переданный type_label из API, если он есть
        if (e.type_label) {
            typeLabel = e.type_label;
        }

        return `
        <div class="error-item ${errorClass}">
            <div class="error-header">
                <span class="error-type">${esc(typeLabel)}</span>
                <span class="error-time">${esc(e.time || '—')}</span>
            </div>
            <div class="error-message">${esc(e.message || '—')}</div>
        </div>`;
    }).join('');

    // Применяем фильтр если активен
    if (state.errorTab !== 'all') filterErrors(state.errorTab);
}


function updateChunks(data) {
    const info = document.getElementById('heatmap-info');
    if (info) info.textContent = `${data.chunks_active || 0} чанков активно, ${data.chunks_loaded || 0} загружено`;
}

function updateUsers(data) {
    const users = data.online_users || [];
    const tbody = document.querySelector('#users-online-table tbody');
    if (!tbody) return;
    if (users.length === 0) {
        tbody.innerHTML = `<tr><td colspan="4" style="text-align:center;padding:20px;color:var(--text-dim);">Нет пользователей онлайн</td></tr>`;
        return;
    }
    tbody.innerHTML = users.map(u => `
        <tr>
            <td>${esc(u.name || u.email || '—')}</td>
            <td>${esc(u.role || '—')}</td>
            <td style="font-family:var(--font-mono);">${esc(u.last_seen || '—')}</td>
            <td>${esc(u.status || '🟢 Онлайн')}</td>
        </tr>`).join('');
}

function updateDatabase(data) {
    setText('db-worldobjects', data.db_worldobjects || data.objects_total || '—');
    setText('db-chunks', data.db_chunks || data.chunks_total || '—');
    setText('db-assets', data.db_assets || data.assets_total || '—');
    setText('db-tools', data.db_tools || data.tools_active || '—');
    setText('db-users', data.db_users || data.users_total || '—');

    const total = (data.objects_total || 0) + (data.chunks_total || 0) + (data.assets_total || 0) + (data.tools_active || 0) + (data.users_total || 0);
    setText('stat-db-total-records', total);
}

// ==============================
// УТИЛИТЫ
// ==============================
function setText(id, value) {
    const el = document.getElementById(id);
    if (el && value !== undefined) el.textContent = value;
}

function updateBar(id, percent) {
    const bar = document.getElementById(id);
    if (!bar) return;
    bar.style.width = Math.min(100, Math.max(0, percent)) + '%';
    bar.style.background = percent > 80 ? 'var(--danger)' : percent > 60 ? 'var(--warning)' : 'var(--success)';
}

function esc(str) {
    const div = document.createElement('div');
    div.textContent = str || '';
    return div.innerHTML;
}