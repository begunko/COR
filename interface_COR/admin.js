/**
 * ================================================================
 * COR ENGINE — Admin Panel Logic
 * ================================================================
 * 
 * ОРИЕНТИРЫ:
 * - Grafana: реалтайм обновление метрик
 * - Chrome DevTools: консоль ошибок
 * - Datadog: алерты
 * 
 * ЧТО МЫ ИЗБЕГАЕМ:
 * - Терминала (безопасность)
 * - Прямого доступа к Django Admin
 * 
 * К ЧЕМУ СТРЕМИМСЯ:
 * - WebSocket реалтайм
 * - Алерты при перегрузке чанков
 * ================================================================
 */

'use strict';

const state = {
    tab: 'overview',
    errorTab: 'all',
};

// ---- Переключение вкладок (меню) ----
document.querySelectorAll('.tree-item[data-menu]').forEach(item => {
    item.addEventListener('click', () => {
        document.querySelectorAll('.tree-item[data-menu]').forEach(i => i.classList.remove('active'));
        item.classList.add('active');
        state.tab = item.dataset.menu;
        showTab(state.tab);
    });
});

// ---- Переключение вкладок (тулбар) ----
document.querySelectorAll('#top-toolbar .toolbar-btn[data-tab]').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('#top-toolbar .toolbar-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        state.tab = btn.dataset.tab;
        showTab(state.tab);
        // Синхронизация с меню
        document.querySelectorAll('.tree-item[data-menu]').forEach(i => i.classList.remove('active'));
        const menuItem = document.querySelector(`.tree-item[data-menu="${state.tab}"]`);
        if (menuItem) menuItem.classList.add('active');
    });
});

function showTab(tabName) {
    document.querySelectorAll('.admin-tab').forEach(tab => tab.style.display = 'none');
    const tab = document.getElementById(`tab-${tabName}`);
    if (tab) tab.style.display = 'block';
}

// ---- Переключение под-вкладок ошибок ----
document.querySelectorAll('.outliner-tab[data-error-tab]').forEach(tab => {
    tab.addEventListener('click', () => {
        document.querySelectorAll('.outliner-tab[data-error-tab]').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        state.errorTab = tab.dataset.errorTab;
        filterErrors(state.errorTab);
    });
});

function filterErrors(type) {
    document.querySelectorAll('.error-item').forEach(item => {
        if (type === 'all') {
            item.style.display = 'block';
        } else {
            item.style.display = item.classList.contains(`error-${type}`) ? 'block' : 'none';
        }
    });
}

// ---- Роль ----
initRoleBadge(
    document.getElementById('role-badge'),
    document.getElementById('role-modal'),
    document.getElementById('apply-role-btn'),
    (role) => console.log('👤 Роль:', role)
);

// ---- Симуляция метрик (в будущем WebSocket) ----
function updateMetrics() {
    const cpu = Math.floor(Math.random() * 30) + 10;
    document.getElementById('cpu-usage').textContent = cpu + '%';
    document.getElementById('cpu-usage').parentElement.querySelector('.stat-bar-fill').style.width = cpu + '%';

    document.getElementById('sql-rate').textContent = Math.floor(Math.random() * 100) + 80;
}

setInterval(updateMetrics, 3000);
updateMetrics();

console.log('💻 Admin Panel v1.0');
console.log('   📊 Обзор системы');
console.log('   ❌ Ошибки (сервер/чанки/браузер)');
console.log('   🍯 Тепловая карта чанков');
console.log('   👥 Пользователи (FPS/пинг)');
console.log('   🗄 Статистика БД');