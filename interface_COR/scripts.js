/**
 * ================================================================
 * COR ENGINE UI Прототип v2.1 — Логика интерфейса
 * ================================================================
 * 
 * ОРИЕНТИРЫ (на кого равняемся):
 * ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 * 
 * 🎮 УПРАВЛЕНИЕ ГИЗМО:
 * - Blender: W=Translate, E=Rotate, R=Scale (мы делаем так же!)
 * - Unity: QWERTY раскладка для инструментов
 * - Godot: совмещение мышкой + ручной ввод в инспекторе
 * 
 * 🖱 SNAP-СИСТЕМА:
 * - Unity: Ctrl+Shift для привязки к сетке
 * - Unreal Engine: End для привязки к поверхности
 * - Godot: инструмент Snap в тулбаре
 * 
 * 🎭 РОЛЕВАЯ СИСТЕМА:
 * - Figma: просмотрщик vs редактор (Viewer/Editor)
 * - Discord: роли с разными правами
 * - WordPress: Capabilities система
 * 
 * 💬 ЧАТ:
 * - World of Warcraft: /команды, Enter для активации
 * - CS:GO: полупрозрачный чат в углу экрана
 * - Telegram: быстрый ввод без переключения окон
 *
 * ЧТО МЫ ИЗБЕГАЕМ:
 * ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 * - Дублирования обработчиков (один listener на гизмо)
 * - Хардкода имён (все имена из state/конфига)
 * - Прямой манипуляции DOM.style (используем CSS классы)
 * - Спагетти-кода (каждая функция делает что-то одно)
 * 
 * К ЧЕМУ СТРЕМИМСЯ:
 * ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 * - Чистый publish/subscribe для событий (в будущем)
 * - WebSocket синхронизация состояния
 * - Горячие клавиши как у Blender (настраиваемые)
 * - Undo/Redo система (Command Pattern)
 * - Экспорт/импорт раскладки панелей
 * ================================================================
 */

'use strict';

// ================================================================
// STATE — центральное хранилище состояния UI
// Ориентир: Redux Store, Vuex, Pinia
// Избегаем: разбросанных переменных
// ================================================================
const state = {
    role: 'designer',
    isAdvanced: true,
    isPinned: false,
    gizmoMode: 'translate',
    snapGrid: false,
    snapSurface: false,
    uniformScale: true,
    outlinerCollapsed: false,
    inspectorCollapsed: false,
    chatOpen: false,
    isRecording: false,
};

// ================================================================
// DOM CACHE — кеш ссылок на элементы
// Ориентир: jQuery $, Blender bpy.data
// Избегаем: повторных querySelector
// ================================================================
const DOM = {
    roleBadge: document.getElementById('role-badge'),
    roleModal: document.getElementById('role-modal'),
    applyRoleBtn: document.getElementById('apply-role-btn'),
    inspector: document.getElementById('inspector'),
    outliner: document.getElementById('outliner'),
    profiler: document.getElementById('profiler'),
    gameChat: document.getElementById('game-chat'),
    toggleAdvancedBtn: document.getElementById('toggle-advanced-btn'),
    pinInspectorBtn: document.getElementById('pin-inspector-btn'),
    uniformScaleCheckbox: document.getElementById('uniform-scale'),
    collapseOutlinerBtn: document.getElementById('collapse-outliner-btn'),
    collapseInspectorBtn: document.getElementById('collapse-inspector-btn'),
    snapGridInspBtn: document.getElementById('snap-grid-insp-btn'),
    snapSurfaceInspBtn: document.getElementById('snap-surface-insp-btn'),
    deleteInspBtn: document.getElementById('delete-insp-btn'),
    gridOptions: document.getElementById('grid-options'),
    addPanelBtn: document.getElementById('add-panel-btn'),
    recBtn: document.getElementById('rec-btn'),
    playBtn: document.getElementById('play-btn'),
    pauseBtn: document.getElementById('pause-btn'),
    stopBtn: document.getElementById('stop-btn'),
    chatInput: document.getElementById('chat-input'),
    chatMessages: document.getElementById('chat-messages'),
};

// ================================================================
// ROLE NAMES — человекочитаемые имена ролей
// Ориентир: Discord Role Colors, Figma Permissions
// ================================================================
const ROLE_NAMES = {
    marketer: '📢 Маркетолог',
    artist: '🎨 Художник',
    designer: '🏗 Дизайнер',
    programmer: '💻 Программист',
};

// ================================================================
// 1. GIZMO MODE SWITCHING
// Ориентир: Blender W/E/R, Unity QWERTY
// Избегаем: дублирования в тулбаре (гизмо ТОЛЬКО в инспекторе)
// ================================================================
function setGizmoMode(mode) {
    if (!['translate', 'rotate', 'scale'].includes(mode)) return;

    state.gizmoMode = mode;

    // Обновляем кнопки в инспекторе
    document.querySelectorAll('.tool-btn[data-mode]').forEach(btn => {
        const isActive = btn.dataset.mode === mode;
        btn.classList.toggle('active', isActive);

        // Визуальный фидбек как в Godot: активная кнопка подсвечена
        if (isActive) {
            btn.style.background = 'var(--accent-strong)';
            btn.style.color = '#fff';
            btn.style.borderColor = 'var(--accent)';
            btn.style.boxShadow = '0 0 10px var(--accent-glow)';
        } else {
            btn.style.background = '';
            btn.style.color = '';
            btn.style.borderColor = '';
            btn.style.boxShadow = '';
        }
    });

    // Логируем (в будущем: отправляем через WebSocket)
    console.log(`🛠 Гизмо: ${mode}`);
}

// Привязываем обработчики к кнопкам в инспекторе
document.querySelectorAll('.tool-btn[data-mode]').forEach(btn => {
    btn.addEventListener('click', () => setGizmoMode(btn.dataset.mode));
});

// ================================================================
// 2. SNAP TO GRID
// Ориентир: Unity Grid Snapping, Blender Absolute Grid Snap
// Избегаем: невидимого состояния (всегда показываем активно/нет)
// ================================================================
function toggleSnapGrid() {
    state.snapGrid = !state.snapGrid;
    const btn = DOM.snapGridInspBtn;

    if (state.snapGrid) {
        btn.classList.add('active');
        btn.style.background = 'var(--accent-strong)';
        btn.style.color = '#fff';
        btn.style.borderColor = 'var(--accent)';
        btn.style.boxShadow = '0 0 10px var(--accent-glow)';
        DOM.gridOptions.style.display = 'block';
    } else {
        btn.classList.remove('active');
        btn.style.background = '';
        btn.style.color = '';
        btn.style.borderColor = '';
        btn.style.boxShadow = '';
        DOM.gridOptions.style.display = 'none';
    }

    console.log(`🧲 Snap Grid: ${state.snapGrid ? 'ON' : 'OFF'}`);
}

DOM.snapGridInspBtn.addEventListener('click', toggleSnapGrid);

// ================================================================
// 3. SNAP TO SURFACE
// Ориентир: Unreal Engine Surface Snapping, Godot Floor Constraint
// Особенность: объект "падает" на ближайшую поверхность под ним
// ================================================================
function toggleSnapSurface() {
    state.snapSurface = !state.snapSurface;
    const btn = DOM.snapSurfaceInspBtn;

    if (state.snapSurface) {
        btn.classList.add('active');
        btn.style.background = 'var(--accent-strong)';
        btn.style.color = '#fff';
        btn.style.borderColor = 'var(--accent)';
        btn.style.boxShadow = '0 0 10px var(--accent-glow)';
    } else {
        btn.classList.remove('active');
        btn.style.background = '';
        btn.style.color = '';
        btn.style.borderColor = '';
        btn.style.boxShadow = '';
    }

    console.log(`⤓ Snap Surface: ${state.snapSurface ? 'ON' : 'OFF'}`);
}

DOM.snapSurfaceInspBtn.addEventListener('click', toggleSnapSurface);

// ================================================================
// 4. DELETE
// Ориентир: Blender X/Delete, Unity Delete
// Особенность: запрос подтверждения (как в Blender)
// ================================================================
function handleDelete() {
    // В будущем: проверка через WebSocket lock
    if (confirm('Удалить выделенный объект?\nЭта операция обратима через Undo.')) {
        console.log('🗑 Объект удалён');
        // В будущем: RealtimeSync.sendDelete()
    }
}

DOM.deleteInspBtn.addEventListener('click', handleDelete);

// ================================================================
// 5. UNIFORM SCALE
// Ориентир: Godot Transform, Blender Scale Lock
// Особенность: блокирует Y и Z при изменении X
// ================================================================
function updateUniformScale() {
    state.uniformScale = DOM.uniformScaleCheckbox.checked;
    const lockedInputs = document.querySelectorAll('.scale-locked');

    lockedInputs.forEach(inp => {
        inp.disabled = state.uniformScale;
        inp.style.opacity = state.uniformScale ? '0.5' : '1';
        inp.style.cursor = state.uniformScale ? 'not-allowed' : 'text';
    });

    console.log(`🔗 Uniform Scale: ${state.uniformScale ? 'ON' : 'OFF'}`);
}

DOM.uniformScaleCheckbox.addEventListener('change', updateUniformScale);
// Инициализация при загрузке
updateUniformScale();

// ================================================================
// 6. BASIC / ADVANCED MODE
// Ориентир: Godot Editor Settings, Unity Pro/Personal
// Стремимся: новичок видит 3 поля, профи — всё
// ================================================================
function toggleAdvanced() {
    state.isAdvanced = !state.isAdvanced;
    const btn = DOM.toggleAdvancedBtn;
    const sections = document.querySelectorAll('.advanced-section');

    sections.forEach(section => {
        section.style.display = state.isAdvanced ? 'block' : 'none';
    });

    // Визуальный фидбек
    btn.classList.toggle('pinned', state.isAdvanced);
    btn.textContent = state.isAdvanced ? '⚙' : '🔰';
    btn.title = state.isAdvanced ? 'Advanced режим' : 'Basic режим';

    console.log(`⚙ Режим: ${state.isAdvanced ? 'Advanced' : 'Basic'}`);
}

DOM.toggleAdvancedBtn.addEventListener('click', toggleAdvanced);

// ================================================================
// 7. PIN INSPECTOR
// Ориентир: Unity Lock Inspector, Chrome DevTools Pin
// Особенность: закрепляет инспектор за выбранным объектом
// ================================================================
function togglePinInspector() {
    state.isPinned = !state.isPinned;
    const btn = DOM.pinInspectorBtn;

    btn.classList.toggle('pinned', state.isPinned);
    btn.textContent = state.isPinned ? '📌' : '📌';

    // Визуальная индикация: locked поля
    const inputs = DOM.inspector.querySelectorAll('input[type="text"]');
    inputs.forEach(inp => {
        if (state.isPinned) {
            inp.style.borderColor = 'var(--accent)';
            inp.style.background = 'rgba(255,102,0,0.05)';
        } else {
            inp.style.borderColor = '';
            inp.style.background = '';
        }
    });

    console.log(`📌 Inspector ${state.isPinned ? 'закреплён' : 'откреплён'}`);
}

DOM.pinInspectorBtn.addEventListener('click', togglePinInspector);

// ================================================================
// 8. COLLAPSE PANELS
// Ориентир: VSCode Sidebar, Blender Toggle Panels (T/N)
// Избегаем: удаления панели (только скрытие)
// ================================================================
function collapseOutliner() {
    state.outlinerCollapsed = !state.outlinerCollapsed;
    const btn = DOM.collapseOutlinerBtn;

    if (state.outlinerCollapsed) {
        DOM.outliner.style.width = '36px';
        DOM.outliner.querySelector('.panel-content').style.display = 'none';
        DOM.outliner.querySelector('.outliner-tabs').style.display = 'none';
        btn.textContent = '▶';
        btn.title = 'Развернуть';
    } else {
        DOM.outliner.style.width = '260px';
        DOM.outliner.querySelector('.panel-content').style.display = 'block';
        DOM.outliner.querySelector('.outliner-tabs').style.display = 'flex';
        btn.textContent = '◀';
        btn.title = 'Свернуть';
    }
}

function collapseInspector() {
    state.inspectorCollapsed = !state.inspectorCollapsed;
    const btn = DOM.collapseInspectorBtn;

    if (state.inspectorCollapsed) {
        DOM.inspector.style.width = '36px';
        DOM.inspector.querySelector('.panel-content').style.display = 'none';
        btn.textContent = '◀';
        btn.title = 'Развернуть';
    } else {
        DOM.inspector.style.width = '280px';
        DOM.inspector.querySelector('.panel-content').style.display = 'block';
        btn.textContent = '▶';
        btn.title = 'Свернуть';
    }
}

DOM.collapseOutlinerBtn.addEventListener('click', collapseOutliner);
DOM.collapseInspectorBtn.addEventListener('click', collapseInspector);

// ================================================================
// 9. ROLE SYSTEM
// Ориентир: Figma Roles, Discord Permissions, WordPress Capabilities
// Особенность: каждая роль видит только свои инструменты
// Стремимся: серверная валидация прав
// ================================================================
function openRoleModal() {
    DOM.roleModal.style.display = 'flex';
}

function closeRoleModal() {
    DOM.roleModal.style.display = 'none';
}

function selectRole(role) {
    document.querySelectorAll('.modal-option').forEach(opt => {
        opt.classList.toggle('selected', opt.dataset.role === role);
    });
}

function applyRole() {
    const selected = document.querySelector('.modal-option.selected');
    if (!selected) return;

    state.role = selected.dataset.role;
    updateUIForRole(state.role);
    closeRoleModal();

    console.log(`👤 Роль изменена: ${ROLE_NAMES[state.role]}`);
}

// Обработчики модалки
DOM.roleBadge.addEventListener('click', openRoleModal);
DOM.applyRoleBtn.addEventListener('click', applyRole);
DOM.roleModal.addEventListener('click', (e) => {
    if (e.target === DOM.roleModal) closeRoleModal();
});

// Выбор роли кликом
document.querySelectorAll('.modal-option').forEach(opt => {
    opt.addEventListener('click', () => selectRole(opt.dataset.role));
});

/**
 * Обновление интерфейса под роль
 * Ориентир: WordPress Admin Bar (разное меню для разных ролей)
 */
function updateUIForRole(role) {
    DOM.roleBadge.textContent = ROLE_NAMES[role] || '🎭 Гость';

    const allButtons = document.querySelectorAll('#top-toolbar .toolbar-btn');
    const playBtn = DOM.playBtn;
    const recBtn = DOM.recBtn;

    switch (role) {
        case 'marketer':
            // ТОЛЬКО Viewport + Play + Rec
            DOM.inspector.style.display = 'none';
            DOM.outliner.style.display = 'none';
            DOM.profiler.style.display = 'none';
            DOM.gameChat.style.display = 'none';
            allButtons.forEach(b => b.style.display = 'none');
            playBtn.style.display = '';
            recBtn.style.display = '';
            break;

        case 'artist':
            // Всё кроме гизмо и скриптов
            DOM.inspector.style.display = '';
            DOM.outliner.style.display = '';
            DOM.profiler.style.display = '';
            DOM.gameChat.style.display = '';
            allButtons.forEach(b => b.style.display = (b === recBtn) ? 'none' : '');
            document.querySelectorAll('.advanced-section').forEach(el => el.style.display = 'none');
            break;

        case 'designer':
            // Полный доступ к сцене
            DOM.inspector.style.display = '';
            DOM.outliner.style.display = '';
            DOM.profiler.style.display = '';
            DOM.gameChat.style.display = '';
            allButtons.forEach(b => b.style.display = '');
            document.querySelectorAll('.advanced-section').forEach(el => {
                el.style.display = state.isAdvanced ? 'block' : 'none';
            });
            break;

        case 'programmer':
            // Всё + инструменты разработчика
            DOM.inspector.style.display = '';
            DOM.outliner.style.display = '';
            DOM.profiler.style.display = '';
            DOM.gameChat.style.display = '';
            allButtons.forEach(b => b.style.display = (b === recBtn) ? 'none' : '');
            document.querySelectorAll('.advanced-section').forEach(el => el.style.display = 'block');
            break;
    }
}

// ================================================================
// 10. CHAT SYSTEM
// Ориентир: World of Warcraft (/say, /party), Discord Enter-to-chat
// Особенность: Enter активирует чат, Escape — деактивирует
// ================================================================
function activateChat() {
    state.chatOpen = true;
    DOM.chatInput.focus();
    DOM.gameChat.style.borderColor = 'var(--accent)';
    DOM.chatInput.placeholder = 'Введите сообщение...';
}

function deactivateChat() {
    state.chatOpen = false;
    DOM.chatInput.blur();
    DOM.gameChat.style.borderColor = '';
    DOM.chatInput.placeholder = 'Нажми Enter для чата...';
}

function sendChatMessage() {
    const text = DOM.chatInput.value.trim();
    if (!text) return;

    const roleName = ROLE_NAMES[state.role]?.split(' ')[1] || 'Я';
    const msg = document.createElement('div');
    msg.className = 'chat-msg fade-in';
    msg.innerHTML = `<span class="user">${roleName}:</span> ${escapeHTML(text)}`;

    DOM.chatMessages.appendChild(msg);
    DOM.chatMessages.scrollTop = DOM.chatMessages.scrollHeight;
    DOM.chatInput.value = '';

    // В будущем: отправка через WebSocket
    console.log(`💬 Чат: ${roleName}: ${text}`);
}

function escapeHTML(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

// Глобальный перехват Enter
document.addEventListener('keydown', (e) => {
    if (e.target.tagName === 'INPUT' && e.target !== DOM.chatInput) return;
    if (e.target.tagName === 'TEXTAREA') return;
    if (e.target.tagName === 'SELECT') return;

    if (e.key === 'Enter' && !state.chatOpen) {
        e.preventDefault();
        activateChat();
    }
    if (e.key === 'Escape' && state.chatOpen) {
        deactivateChat();
    }
});

// Отправка сообщения
DOM.chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        e.preventDefault();
        sendChatMessage();
    }
    if (e.key === 'Escape') {
        deactivateChat();
    }
});

// ================================================================
// 11. FPS SIMULATION
// Ориентир: Unity Stats, Godot Performance Monitor
// Стремимся: реальные данные от Babylon.js engine
// ================================================================
function simulateFPS() {
    const fps = 45 + Math.floor(Math.random() * 20);
    const drawcalls = 100 + Math.floor(Math.random() * 60);

    const fpsEl = document.getElementById('fps-value');
    const dcEl = document.getElementById('drawcalls-value');
    const fpsBar = document.getElementById('fps-bar');

    fpsEl.textContent = fps;
    dcEl.textContent = drawcalls;

    // Цвет индикатора: зелёный > 55, жёлтый > 35, красный < 35
    const status = fps >= 55 ? 'good' : fps >= 35 ? 'warn' : 'bad';
    fpsEl.className = `value ${status}`;
    fpsBar.style.width = (fps / 60 * 100) + '%';
    fpsBar.className = `profiler-bar-fill ${status === 'warn' ? 'warn' : status === 'bad' ? 'bad' : ''}`;
}

setInterval(simulateFPS, 1500);
simulateFPS();

// ================================================================
// 12. ADD PANEL (+)
// Ориентир: VSCode Panel System, Blender Editor Type
// Стремимся: динамическое добавление панелей из БД
// ================================================================
function addPanel() {
    // В будущем: открывать меню выбора панели
    const message = [
        '➕ Добавление панелей (будет реализовано):',
        '',
        '📋 Второй Инспектор (для сравнения объектов)',
        '📦 Content Browser (drag-n-drop ассетов)',
        '🔗 Node Editor (материалы и логика)',
        '📝 Script Editor (Monaco/VSCode)',
        '🦴 Character Editor (скелет и анимации)',
        '',
        '💡 Все панели берутся из БД и настраиваются под роль.'
    ].join('\n');

    alert(message);
    console.log('➕ Панель: пользователь открыл меню добавления');
}

DOM.addPanelBtn.addEventListener('click', addPanel);

// ================================================================
// 13. RECORDING
// Ориентир: OBS Studio, Nvidia ShadowPlay
// Особенность: WebCodecs API для записи в браузере
// ================================================================
function toggleRecording() {
    state.isRecording = !state.isRecording;
    const btn = DOM.recBtn;

    if (state.isRecording) {
        btn.textContent = '⏹';
        btn.title = 'Остановить запись';
        btn.style.color = 'var(--danger)';
        btn.style.borderColor = 'var(--danger)';
        console.log('⏺ Запись началась...');
    } else {
        btn.textContent = '⏺';
        btn.title = 'Записать';
        btn.style.color = '';
        btn.style.borderColor = '';
        console.log('⏹ Запись остановлена');
    }
}

DOM.recBtn.addEventListener('click', toggleRecording);

// ================================================================
// 14. OUTLINER TABS
// Ориентир: Blender Tabs (Scene/World), Unity Project/Console
// ================================================================
function switchOutlinerTab(tabName) {
    // Обновляем активную вкладку
    document.querySelectorAll('.outliner-tab').forEach(t => {
        t.classList.toggle('active', t.dataset.tab === tabName);
    });

    // Показываем нужный контент
    ['world', 'prefabs', 'graph'].forEach(name => {
        const el = document.getElementById(`tab-${name}`);
        if (el) el.style.display = name === tabName ? 'block' : 'none';
    });

    console.log(`🌍 Outliner: вкладка "${tabName}"`);
}

document.querySelectorAll('.outliner-tab').forEach(tab => {
    tab.addEventListener('click', () => switchOutlinerTab(tab.dataset.tab));
});

// ================================================================
// 15. KEYBOARD SHORTCUTS
// Ориентир: Blender Keymap, VSCode Keyboard Shortcuts
// Стремимся: настраиваемые горячие клавиши
// ================================================================
document.addEventListener('keydown', (e) => {
    // Не перехватываем если фокус в поле ввода
    if (e.target.tagName === 'INPUT' && e.target !== DOM.chatInput) return;
    if (e.target.tagName === 'TEXTAREA') return;
    if (e.target.tagName === 'SELECT') return;

    const key = e.key.toLowerCase();

    switch (key) {
        case 'w': setGizmoMode('translate'); break;
        case 'e': setGizmoMode('rotate'); break;
        case 'r': setGizmoMode('scale'); break;
        case 'delete':
        case 'backspace':
            e.preventDefault();
            handleDelete();
            break;
        case 'escape':
            deselectAll();
            if (state.chatOpen) deactivateChat();
            break;
        case 'g':
            if (!e.ctrlKey && !e.metaKey) {
                toggleSnapGrid();
            }
            break;
        default:
            break;
    }
});

/**
 * Снять выделение со всех объектов
 * Ориентир: Blender Alt+A (Deselect All)
 */
function deselectAll() {
    document.querySelectorAll('.tree-item.selected').forEach(el => {
        el.classList.remove('selected');
    });
    console.log('⬜ Выделение снято');
}

// ================================================================
// PLAY / PAUSE / STOP
// Ориентир: Unity Play/Pause/Stop, Godot Run/Stop
// ================================================================
DOM.playBtn.addEventListener('click', () => {
    console.log('▶ Запуск игры...');
    DOM.playBtn.style.display = 'none';
    DOM.pauseBtn.style.display = '';
    DOM.stopBtn.style.display = '';
});

DOM.pauseBtn.addEventListener('click', () => {
    console.log('⏸ Пауза');
    DOM.pauseBtn.style.display = 'none';
    DOM.playBtn.style.display = '';
    DOM.playBtn.textContent = '⏯';
});

DOM.stopBtn.addEventListener('click', () => {
    console.log('■ Остановка');
    DOM.stopBtn.style.display = 'none';
    DOM.pauseBtn.style.display = 'none';
    DOM.playBtn.style.display = '';
    DOM.playBtn.textContent = '▶';
});

// ================================================================
// INITIALIZATION
// ================================================================
function init() {
    console.log('🚀 COR Engine UI Прототип v2.1');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('👤 Роль:', ROLE_NAMES[state.role]);
    console.log('⚙ Режим:', state.isAdvanced ? 'Advanced' : 'Basic');
    console.log('📌 Pin:', state.isPinned);
    console.log('🧲 Snap Grid:', state.snapGrid);
    console.log('⤓ Snap Surface:', state.snapSurface);
    console.log('🔗 Uniform Scale:', state.uniformScale);
    console.log('🛠 Гизмо:', state.gizmoMode);
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('💡 Нажми на значок роли чтобы переключить');
    console.log('⌨ W/E/R — гизмо | G — сетка | Delete — удалить');
    console.log('💬 Enter — чат | Esc — снять выделение');

    // Прячем кнопки паузы и стопа при старте
    DOM.pauseBtn.style.display = 'none';
    DOM.stopBtn.style.display = 'none';

    // Применяем начальную роль
    updateUIForRole(state.role);
}

init();