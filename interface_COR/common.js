/**
 * ================================================================
 * COR ENGINE — Common Module (общий для всех редакторов)
 * ================================================================
 * 
 * ОРИЕНТИРЫ:
 * - DRY (Don't Repeat Yourself): выносим повторяющийся код
 * - jQuery: удобные утилиты для DOM
 * - VSCode API: общие сервисы
 * 
 * ЧТО МЫ ИЗБЕГАЕМ:
 * - Копипасты между editor'ами
 * - Разных реализаций одного и того же
 * 
 * К ЧЕМУ СТРЕМИМСЯ:
 * - Единый модуль для Snap, Gizmo, Inspector, клавиш
 * - Подключение в любом редакторе
 * ================================================================
 */

'use strict';

// ================================================================
// 1. GIZMO MODE
// ================================================================
function createGizmoController(state, selector = '.tool-btn[data-mode]') {
    return {
        setMode(mode) {
            if (!['translate', 'rotate', 'scale'].includes(mode)) return;
            state.gizmoMode = mode;

            document.querySelectorAll(selector).forEach(btn => {
                const isActive = btn.dataset.mode === mode;
                btn.classList.toggle('active', isActive);
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
        },
        bindButtons() {
            document.querySelectorAll(selector).forEach(btn => {
                btn.addEventListener('click', () => this.setMode(btn.dataset.mode));
            });
        }
    };
}

// ================================================================
// 2. SNAP GRID
// ================================================================
function createSnapGridController(state, btn, gridOptionsEl) {
    return {
        toggle() {
            state.snapGrid = !state.snapGrid;
            if (state.snapGrid) {
                btn.classList.add('active');
                btn.style.background = 'var(--accent-strong)';
                btn.style.color = '#fff';
                btn.style.borderColor = 'var(--accent)';
                btn.style.boxShadow = '0 0 10px var(--accent-glow)';
                if (gridOptionsEl) gridOptionsEl.style.display = 'block';
            } else {
                btn.classList.remove('active');
                btn.style.background = '';
                btn.style.color = '';
                btn.style.borderColor = '';
                btn.style.boxShadow = '';
                if (gridOptionsEl) gridOptionsEl.style.display = 'none';
            }
        }
    };
}

// ================================================================
// 3. SNAP SURFACE
// ================================================================
function createSnapSurfaceController(state, btn) {
    return {
        toggle() {
            state.snapSurface = !state.snapSurface;
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
        }
    };
}

// ================================================================
// 4. COLLAPSE PANEL
// ================================================================
function createCollapseController(panelSelector, contentSelector, tabsSelector, btn, defaultWidth = '260px', collapsedWidth = '36px') {
    let collapsed = false;

    return {
        toggle() {
            collapsed = !collapsed;
            const panel = document.querySelector(panelSelector);
            const content = panel?.querySelector(contentSelector);
            const tabs = panel?.querySelector(tabsSelector);

            if (panel) panel.style.width = collapsed ? collapsedWidth : defaultWidth;
            if (content) content.style.display = collapsed ? 'none' : 'block';
            if (tabs) tabs.style.display = collapsed ? 'none' : 'flex';
            if (btn) btn.textContent = collapsed ? '▶' : '◀';
        }
    };
}

// ================================================================
// 5. KEYBOARD SHORTCUTS
// ================================================================
function createKeyboardController(handlers) {
    return {
        bind() {
            document.addEventListener('keydown', (e) => {
                if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.tagName === 'SELECT') return;

                const key = e.key.toLowerCase();

                if (handlers[key]) {
                    e.preventDefault();
                    handlers[key](e);
                }
            });
        }
    };
}

// ================================================================
// 6. ADVANCED TOGGLE
// ================================================================
function createAdvancedController(state, btn) {
    return {
        toggle() {
            state.isAdvanced = !state.isAdvanced;
            document.querySelectorAll('.advanced-section').forEach(el => {
                el.style.display = state.isAdvanced ? 'block' : 'none';
            });
            if (btn) {
                btn.classList.toggle('pinned', state.isAdvanced);
                btn.textContent = state.isAdvanced ? '⚙' : '🔰';
                btn.title = state.isAdvanced ? 'Advanced режим' : 'Basic режим';
            }
        }
    };
}

// ================================================================
// 7. PIN TOGGLE
// ================================================================
function createPinController(state, btn, inputsSelector = '#inspector input[type="text"]') {
    return {
        toggle() {
            state.isPinned = !state.isPinned;
            if (btn) {
                btn.classList.toggle('pinned', state.isPinned);
            }
            document.querySelectorAll(inputsSelector).forEach(inp => {
                if (state.isPinned) {
                    inp.style.borderColor = 'var(--accent)';
                    inp.style.background = 'rgba(255,102,0,0.05)';
                } else {
                    inp.style.borderColor = '';
                    inp.style.background = '';
                }
            });
        }
    };
}

// ================================================================
// 8. ROLE BADGE (общий для всех)
// ================================================================
function initRoleBadge(roleBadgeEl, roleModalEl, applyBtnEl, onRoleChange) {
    const ROLE_NAMES = {
        marketer: '📢 Маркетолог',
        artist: '🎨 Художник',
        designer: '🏗 Дизайнер',
        programmer: '💻 Программист',
    };

    let currentRole = 'designer';

    function openModal() { roleModalEl.style.display = 'flex'; }
    function closeModal() { roleModalEl.style.display = 'none'; }

    function applyRole() {
        const selected = roleModalEl.querySelector('.modal-option.selected');
        if (!selected) return;
        currentRole = selected.dataset.role;
        roleBadgeEl.textContent = ROLE_NAMES[currentRole] || '🎭 Гость';
        closeModal();
        if (onRoleChange) onRoleChange(currentRole);
    }

    roleBadgeEl.addEventListener('click', openModal);
    if (applyBtnEl) applyBtnEl.addEventListener('click', applyRole);
    roleModalEl.addEventListener('click', (e) => {
        if (e.target === roleModalEl) closeModal();
    });

    roleModalEl.querySelectorAll('.modal-option').forEach(opt => {
        opt.addEventListener('click', () => {
            roleModalEl.querySelectorAll('.modal-option').forEach(o => o.classList.remove('selected'));
            opt.classList.add('selected');
        });
    });

    return { ROLE_NAMES, getRole: () => currentRole };
}

// ================================================================
// 9. ESCAPE HTML
// ================================================================
function escapeHTML(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

// Экспорт для модульного использования
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        createGizmoController,
        createSnapGridController,
        createSnapSurfaceController,
        createCollapseController,
        createKeyboardController,
        createAdvancedController,
        createPinController,
        initRoleBadge,
        escapeHTML,
    };
}