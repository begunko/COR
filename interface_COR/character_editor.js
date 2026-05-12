/**
 * ================================================================
 * COR ENGINE — Character Editor Logic v2.0
 * ================================================================
 */

'use strict';

const state = {
    mode: 'object',
    selectedBone: 'RightHand',
    currentAnimation: 'Attack',
    currentFrame: 5,
    totalFrames: 60,
    isPinned: false,
};

// ---- Режимы ----
document.querySelectorAll('.mode-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        state.mode = btn.dataset.mode;
        updateModeUI();
    });
});

function updateModeUI() {
    const weightSection = document.getElementById('weight-paint-section');
    const animSection = document.getElementById('animation-section');
    if (weightSection) weightSection.style.display = state.mode === 'weight' ? 'block' : 'none';
    if (animSection) animSection.style.display = state.mode === 'animate' ? 'block' : 'none';
    console.log(`🦴 Режим: ${state.mode}`);
}

// ---- Кости ----
document.querySelectorAll('.bone-item').forEach(item => {
    item.addEventListener('click', (e) => {
        document.querySelectorAll('.bone-item').forEach(b => b.classList.remove('selected'));
        item.classList.add('selected');
        const boneName = item.textContent.replace(/[▼🦴\s]/g, '').trim();
        if (boneName) {
            state.selectedBone = boneName;
            console.log(`👆 Кость: ${boneName}`);
        }
        e.stopPropagation();
    });
});

// ---- Сохранение ----
document.getElementById('save-character-btn')?.addEventListener('click', () => {
    alert('✅ Персонаж сохранён.');
});

// ---- Экспорт ----
document.getElementById('export-fbx-btn')?.addEventListener('click', () => {
    alert('📤 Экспорт в glTF.\nВключает: меш, скелет, веса, анимации.');
});

// ---- Назад ----
document.getElementById('back-to-world-btn')?.addEventListener('click', () => {
    if (confirm('Вернуться в редактор мира?')) window.location.href = 'index.html';
});

// ---- Умные поля ----
setTimeout(() => {
    if (typeof enableAllSmartInputs === 'function') enableAllSmartInputs();
}, 100);

console.log('🦴 Character Editor v2.0');