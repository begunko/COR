/**
 * ================================================================
 * COR ENGINE — Tool Editor Logic v2.0 (модульная версия)
 * ================================================================
 */

'use strict';

// ---- СОСТОЯНИЕ ----
const state = {
    objects: [],
    selectedIndex: -1,
    isAdvanced: true,
    isPinned: false,
    gizmoMode: 'translate',
    snapGrid: false,
    snapSurface: false,
    geometryCollapsed: false,
    inspectorCollapsed: false,
};

// ---- DOM ----
const DOM = {
    geometryList: document.getElementById('geometry-list'),
    geometrySearch: document.getElementById('geometry-search'),
    sceneObjectsList: document.getElementById('scene-objects-list'),
    objectsCount: document.getElementById('objects-count'),
    createGroupBtn: document.getElementById('create-group-btn'),
    saveToolBtn: document.getElementById('save-tool-btn'),
    saveAsBtn: document.getElementById('save-as-btn'),
    exportGlbBtn: document.getElementById('export-glb-btn'),
    backToWorldBtn: document.getElementById('back-to-world-btn'),
    toggleAdvancedBtn: document.getElementById('toggle-advanced-btn'),
    pinInspectorBtn: document.getElementById('pin-inspector-btn'),
    collapseGeometryBtn: document.getElementById('collapse-geometry-btn'),
    collapseInspectorBtn: document.getElementById('collapse-inspector-btn'),
    deleteInspBtn: document.getElementById('delete-insp-btn'),
    snapGridInspBtn: document.getElementById('snap-grid-insp-btn'),
    snapSurfaceInspBtn: document.getElementById('snap-surface-insp-btn'),
    gridOptions: document.getElementById('grid-options') || document.querySelector('.grid-options'),
};

// ---- ИНИЦИАЛИЗИРУЕМ ОБЩИЕ МОДУЛИ ----
const gizmo = createGizmoController(state, '.tool-btn[data-mode]');
gizmo.bindButtons();

const snapGridCtrl = createSnapGridController(state, DOM.snapGridInspBtn, DOM.gridOptions);
DOM.snapGridInspBtn?.addEventListener('click', () => snapGridCtrl.toggle());

const snapSurfaceCtrl = createSnapSurfaceController(state, DOM.snapSurfaceInspBtn);
DOM.snapSurfaceInspBtn?.addEventListener('click', () => snapSurfaceCtrl.toggle());

const advancedCtrl = createAdvancedController(state, DOM.toggleAdvancedBtn);
DOM.toggleAdvancedBtn?.addEventListener('click', () => advancedCtrl.toggle());

const pinCtrl = createPinController(state, DOM.pinInspectorBtn);
DOM.pinInspectorBtn?.addEventListener('click', () => pinCtrl.toggle());

const collapseGeom = createCollapseController('#geometry-panel', '.panel-content', '.outliner-tabs', DOM.collapseGeometryBtn, '280px');
DOM.collapseGeometryBtn?.addEventListener('click', () => collapseGeom.toggle());

const collapseInsp = createCollapseController('#inspector', '.panel-content', '', DOM.collapseInspectorBtn, '280px');
DOM.collapseInspectorBtn?.addEventListener('click', () => collapseInsp.toggle());

// ---- КЛАВИШИ ----
createKeyboardController({
    'w': () => gizmo.setMode('translate'),
    'e': () => gizmo.setMode('rotate'),
    'r': () => gizmo.setMode('scale'),
    'delete': () => { if (state.selectedIndex >= 0) removeObject(state.selectedIndex); },
    'backspace': () => { if (state.selectedIndex >= 0) removeObject(state.selectedIndex); },
    'escape': () => { state.selectedIndex = -1; updateSceneList(); },
}).bind();

// ---- ROLE ----
initRoleBadge(
    document.getElementById('role-badge'),
    document.getElementById('role-modal'),
    document.getElementById('apply-role-btn'),
    (role) => console.log('👤 Роль:', role)
);

// ================================================================
// 1. ДОБАВЛЕНИЕ ГЕОМЕТРИИ
// ================================================================
function addObject(geometryName) {
    const displayName = geometryName.replace('Geometry', '');
    const obj = {
        id: `obj_${Date.now()}_${Math.random().toString(36).substr(2, 6)}`,
        name: `${displayName}_${state.objects.length + 1}`,
        geometry: geometryName,
        position: { x: (Math.random() - 0.5) * 4, y: 0, z: (Math.random() - 0.5) * 4 },
        rotation: { x: 0, y: 0, z: 0 },
        scale: { x: 1, y: 1, z: 1 },
        color: '#ff6600',
        params: { width: 1, height: 1, depth: 1, segments: 1 },
    };

    state.objects.push(obj);
    state.selectedIndex = state.objects.length - 1;
    updateSceneList();
    console.log(`➕ Добавлен: ${obj.name} (${geometryName})`);
}

DOM.geometryList?.addEventListener('click', (e) => {
    const item = e.target.closest('.tree-item');
    if (!item) return;
    const geometry = item.dataset.geometry;
    if (geometry) {
        addObject(geometry);
        document.querySelectorAll('#geometry-list .tree-item').forEach(el => el.classList.remove('selected'));
        item.classList.add('selected');
    }
});

// ================================================================
// 2. ПОИСК
// ================================================================
DOM.geometrySearch?.addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase();
    DOM.geometryList.querySelectorAll('.tree-item').forEach(item => {
        item.style.display = item.textContent.toLowerCase().includes(query) ? 'flex' : 'none';
    });
});

// ================================================================
// 3. КАТЕГОРИИ
// ================================================================
document.querySelectorAll('#geometry-panel .outliner-tab, .outliner-tab').forEach(tab => {
    tab.addEventListener('click', () => {
        document.querySelectorAll('.outliner-tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
    });
});

// ================================================================
// 4. СПИСОК ОБЪЕКТОВ
// ================================================================
function updateSceneList() {
    if (DOM.objectsCount) DOM.objectsCount.textContent = state.objects.length;
    if (DOM.createGroupBtn) DOM.createGroupBtn.disabled = state.objects.length < 2;

    if (!DOM.sceneObjectsList) return;

    if (state.objects.length === 0) {
        DOM.sceneObjectsList.innerHTML = '<div style="color:var(--text-dim);font-size:11px;">Пока пусто</div>';
        return;
    }

    DOM.sceneObjectsList.innerHTML = state.objects.map((obj, i) => `
        <div class="group-item ${i === state.selectedIndex ? 'selected' : ''}" 
             style="${i === state.selectedIndex ? 'background:rgba(255,102,0,0.2);border-color:var(--accent);' : ''}">
            <span onclick="selectObject(${i})" style="cursor:pointer;flex:1;">${obj.name}</span>
            <button class="remove-btn" onclick="removeObject(${i})">×</button>
        </div>
    `).join('');
}

function selectObject(index) {
    state.selectedIndex = index;
    updateSceneList();
    console.log(`👆 Выбран: ${state.objects[index]?.name}`);
}

function removeObject(index) {
    const obj = state.objects[index];
    state.objects.splice(index, 1);
    if (state.selectedIndex >= state.objects.length) {
        state.selectedIndex = state.objects.length - 1;
    }
    updateSceneList();
    console.log(`🗑 Удалён: ${obj?.name}`);
}

window.selectObject = selectObject;
window.removeObject = removeObject;

// ================================================================
// 5. ГРУППА
// ================================================================
DOM.createGroupBtn?.addEventListener('click', () => {
    if (state.objects.length < 2) return;
    const group = {
        id: `group_${Date.now()}`,
        name: `Группа_${Date.now().toString(36)}`,
        geometry: 'Group',
        children: [...state.objects],
    };
    state.objects = [group];
    state.selectedIndex = 0;
    updateSceneList();
    console.log(`🔗 Группа: ${group.name} (${group.children.length} объектов)`);
});

// ================================================================
// 6. СОХРАНЕНИЕ
// ================================================================
function buildSaveData(name) {
    return {
        name,
        default_params: {
            geometry: state.objects.length === 1 ? state.objects[0].geometry : 'Group',
            children: state.objects.map(obj => ({
                name: obj.name,
                geometry: obj.geometry,
                position: [obj.position.x, obj.position.y, obj.position.z],
                rotation: [obj.rotation.x, obj.rotation.y, obj.rotation.z],
                scale: [obj.scale.x, obj.scale.y, obj.scale.z],
                color: obj.color,
            })),
        },
    };
}

DOM.saveToolBtn?.addEventListener('click', () => {
    const name = prompt('Название эталона:', 'Мой объект');
    if (!name) return;
    console.log('💾 Эталон:', buildSaveData(name));
    alert(`✅ Эталон "${name}" сохранён!`);
});

DOM.saveAsBtn?.addEventListener('click', () => {
    const name = prompt('Название копии:', 'Мой объект (копия)');
    if (!name) return;
    console.log('📋 Копия:', buildSaveData(name));
    alert(`✅ Копия "${name}" сохранена.`);
});

// ================================================================
// 7. ЭКСПОРТ
// ================================================================
DOM.exportGlbBtn?.addEventListener('click', () => {
    alert('📤 Экспорт в glTF/glb\n\nФункция в разработке.');
});

// ================================================================
// 8. НАЗАД
// ================================================================
DOM.backToWorldBtn?.addEventListener('click', () => {
    if (state.objects.length > 0 && !confirm('Изменения будут потеряны. Продолжить?')) return;
    window.location.href = 'index.html';
});

// ================================================================
// 9. DELETE (инспектор)
// ================================================================
DOM.deleteInspBtn?.addEventListener('click', () => {
    if (state.selectedIndex >= 0 && state.selectedIndex < state.objects.length) {
        removeObject(state.selectedIndex);
    }
});

// ================================================================
// ИНИЦИАЛИЗАЦИЯ
// ================================================================
setTimeout(() => {
    if (typeof enableAllSmartInputs === 'function') enableAllSmartInputs();
}, 100);

console.log('🔧 Tool Editor v2.0 (модульный)');