// static/js/editor.js
import * as BABYLON from './core/BabylonBridge.js';
import { Config } from './core/Config.js';
import { BabylonSceneManager } from './core/BabylonScene.js';
import { ObjectManager } from './core/ObjectManager.js';
import { RealtimeSync } from './core/RealtimeSync.js';
import { BabylonToolbar } from './tools/BabylonToolbar.js';

// ========== СЦЕНА ==========
const sm = new BabylonSceneManager();
sm.init();
const scene = sm.scene;

// *** ВАЖНЫЙ ФИКС: ПЕРЕНОСИМ CANVAS ВНУТРЬ VIEWPORT ***
// Этот блок кода уже есть в entity_editor.html, но отсутствовал здесь
const viewportDiv = document.getElementById('viewport');
if (viewportDiv && sm.canvas) {
    viewportDiv.appendChild(sm.canvas);
    sm.canvas.style.width = '100%';
    sm.canvas.style.height = '100%';
    sm.engine.resize(); // Сообщаем движку, что размер изменился
}

// Глобальный доступ для отладки и внешних вызовов
window.COR = window.COR || {};
window.COR.sceneManager = sm;

// ========== МЕНЕДЖЕР ОБЪЕКТОВ ==========
const om = new ObjectManager(scene, sm.shadowGenerator);

// ========== ВЫДЕЛЕНИЕ ==========
let selected = null;

function getSelected() { return selected; }

scene.onPointerObservable.add((info) => {
    if (info.type !== BABYLON.PointerEventTypes.POINTERPICK) return;
    if (info.event.button !== 0) return;
    const p = info.pickInfo;
    if (p.hit && p.pickedMesh?.metadata && p.pickedMesh.name !== 'ground') selectMesh(p.pickedMesh);
    else deselectAll();
}, BABYLON.PointerEventTypes.POINTERPICK);

function selectMesh(mesh) {
    if (selected === mesh) return;
    deselectAll();
    selected = mesh;
    sm.gizmoManager.attachToMesh(mesh);
    updateInspectorPanel(mesh);
    if (mesh.material?.albedoColor) {
        mesh._savedColor = mesh.material.albedoColor.clone();
        mesh.material.albedoColor = new BABYLON.Color3(1, 0.6, 0);
    }
}

function deselectAll() {
    if (selected) {
        if (selected._savedColor) selected.material.albedoColor = selected._savedColor;
        selected = null;
    }
    sm.gizmoManager.attachToMesh(null);
    updateInspectorPanel(null);
}

// ========== ОБНОВЛЕНИЕ HTML-ПАНЕЛИ ИНСПЕКТОРА ==========
function updateInspectorPanel(mesh) {
    const propsDiv = document.getElementById('inspector-props');
    if (!propsDiv) return;

    if (!mesh) {
        propsDiv.innerHTML = '<div class="inspector-section"><div class="inspector-section-title">Ничего не выбрано</div></div>';
        return;
    }

    const meta = mesh.metadata || {};
    const pos = mesh.position;
    const rot = mesh.rotation;
    const scl = mesh.scaling;

    propsDiv.innerHTML = `
        <div class="inspector-section">
            <div class="inspector-section-title">📍 Позиция</div>
            <div class="inspector-row"><label>X</label><input type="text" value="${pos.x.toFixed(2)}" class="coord-input" disabled></div>
            <div class="inspector-row"><label>Y</label><input type="text" value="${pos.y.toFixed(2)}" class="coord-input" disabled></div>
            <div class="inspector-row"><label>Z</label><input type="text" value="${pos.z.toFixed(2)}" class="coord-input" disabled></div>
        </div>
        <div class="inspector-section">
            <div class="inspector-section-title">🎨 Материал</div>
            <div class="color-preview">
                <div class="color-swatch" style="background:${meta.color || '#ff6600'};"></div>
                <span>${meta.color || '#ff6600'}</span>
            </div>
        </div>
    `;
}

// ========== СИНХРОНИЗАЦИЯ ==========
const sync = new RealtimeSync(om, setStatus, getSelected, deselectAll);
sync.connect();

// ========== ТУЛБАР ==========
const toolbar = new BabylonToolbar(scene, sm, {
    onToolSelected: (tool) => {
        const params = tool.default_params || {};
        const geometry = params.geometry || 'BoxGeometry';

        if (geometry === 'Group' && params.children) {
            const group = new BABYLON.TransformNode(`${tool.name}-${Date.now()}`, scene);
            group.position.set((Math.random() - 0.5) * 4, 0, (Math.random() - 0.5) * 4);
            group.metadata = { id: `${tool.name}-${Date.now()}`, type: 'group', geometry: 'Group', params };
            params.children.forEach(childParams => {
                const childGeom = childParams.geometry || 'BoxGeometry';
                const method = `Create${childGeom.replace('Geometry', '')}`;
                const child = BABYLON.MeshBuilder[method](`child_${Date.now()}`, childParams, scene);
                if (childParams.position) child.position.set(childParams.position[0], childParams.position[1], childParams.position[2]);
                if (childParams.rotation) child.rotation.set(childParams.rotation[0], childParams.rotation[1], childParams.rotation[2]);
                child.material = new BABYLON.PBRMaterial(`mat_${Date.now()}`, scene);
                child.material.albedoColor = BABYLON.Color3.FromHexString(childParams.color || '#ff6600');
                child.material.roughness = 0.4;
                child.material.metallic = 0.1;
                child.isPickable = true;
                child.setParent(group);
            });
            om.allObjects[group.metadata.id] = { mesh: group, metadata: group.metadata };
            sync.sendCreate(group);
            selectMesh(group);
        } else {
            const name = geometry.replace('Geometry', '');
            const method = `Create${name}`;
            const mesh = om.createGeometry(name, method, params, null, params.color,
                new BABYLON.Vector3((Math.random() - 0.5) * 4, params.defaultY || 0.5, (Math.random() - 0.5) * 4));
            sync.sendCreate(mesh);
            selectMesh(mesh);
        }
        sync.scheduleSave();
    },
    onDelete: () => {
        if (!selected) return;
        const id = selected.metadata?.id;
        sync.sendDelete(id);
        om.removeObject(id);
        deselectAll();
        sync.scheduleSave();
    },
    onStatusChange: setStatus,
});

// Загружаем тулбар без старой панели гизмо
toolbar.createWithoutGizmo = function () {
    this.gui = BABYLON.GUI.AdvancedDynamicTexture.CreateFullscreenUI('toolbar-ui');
    this._loadFromDatabase();
};
toolbar.createWithoutGizmo();

// ========== СТАТУС ==========
function setStatus(text, bg) {
    const el = document.getElementById('info');
    if (!el) return;
    el.textContent = text;
    if (bg) el.style.background = bg;
}

// ========== КЛАВИШИ ==========
window.addEventListener('keydown', e => {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    const k = e.key.toLowerCase();
    if (k === 'w') { sm.setGizmoMode('translate'); highlightGizmoButton('translate'); }
    if (k === 'e') { sm.setGizmoMode('rotate'); highlightGizmoButton('rotate'); }
    if (k === 'r') { sm.setGizmoMode('scale'); highlightGizmoButton('scale'); }
    if (k === 'delete' || k === 'backspace') {
        if (selected) { sync.sendDelete(selected.metadata?.id); om.removeObject(selected.metadata?.id); deselectAll(); sync.scheduleSave(); }
    }
    if (k === 'escape') deselectAll();
    if (e.ctrlKey && e.shiftKey && k === 'i') sm.showInspector();
});

// ========== UI ИНИЦИАЛИЗАЦИЯ ==========
function highlightGizmoButton(mode) {
    document.querySelectorAll('#inspector .tool-btn[data-mode]').forEach(b => {
        b.classList.toggle('active', b.dataset.mode === mode);
    });
}

function initUI() {
    // ГИЗМО: Обработчики для кнопок в правой панели
    document.querySelectorAll('#inspector .tool-btn[data-mode]').forEach(btn => {
        btn.addEventListener('click', () => {
            highlightGizmoButton(btn.dataset.mode);
            sm.setGizmoMode(btn.dataset.mode);
        });
    });

    // Кнопка Delete
    const deleteBtn = document.getElementById('delete-insp-btn');
    if (deleteBtn) {
        deleteBtn.addEventListener('click', () => {
            if (!selected) return;
            const id = selected.metadata?.id;
            sync.sendDelete(id);
            om.removeObject(id);
            deselectAll();
            sync.scheduleSave();
        });
    }

    // МОДАЛКА РОЛЕЙ
    const roleBadge = document.getElementById('role-badge');
    const roleModal = document.getElementById('role-modal');
    const applyRoleBtn = document.getElementById('apply-role-btn');

    if (roleBadge && roleModal) {
        roleBadge.addEventListener('click', () => { roleModal.style.display = 'flex'; });
        roleModal.addEventListener('click', (e) => {
            if (e.target === roleModal) roleModal.style.display = 'none';
        });
    }

    if (applyRoleBtn) {
        applyRoleBtn.addEventListener('click', () => {
            const selected = document.querySelector('#role-modal .modal-option.selected');
            if (selected && roleBadge) {
                const role = selected.dataset.role;
                const roleNames = {
                    marketer: '📢 Маркетолог',
                    artist: '🎨 Художник',
                    designer: '🏗 Дизайнер',
                    programmer: '💻 Программист',
                };
                roleBadge.textContent = roleNames[role] || '🎭 Гость';
                roleModal.style.display = 'none';
            }
        });
    }

    document.querySelectorAll('#role-modal .modal-option').forEach(opt => {
        opt.addEventListener('click', () => {
            document.querySelectorAll('#role-modal .modal-option').forEach(o => o.classList.remove('selected'));
            opt.classList.add('selected');
        });
    });

    // СВОРАЧИВАНИЕ ПАНЕЛЕЙ (заглушки)
    document.getElementById('collapse-outliner-btn')?.addEventListener('click', () => {
        const outliner = document.getElementById('outliner');
        if (outliner) outliner.style.display = outliner.style.display === 'none' ? '' : 'none';
    });

    document.getElementById('collapse-inspector-btn')?.addEventListener('click', () => {
        const inspector = document.getElementById('inspector');
        if (inspector) inspector.style.display = inspector.style.display === 'none' ? '' : 'none';
    });
}

// Запускаем UI после полной загрузки всего
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initUI);
} else {
    initUI();
}

// ========== СТАРТ ==========
setStatus('🎮 COR Ready');
console.log('🚀 COR Editor запущен');