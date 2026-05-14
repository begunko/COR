// static/js/editor.js — ЕДИНЫЙ РЕДАКТОР ДЛЯ ВСЕХ РЕЖИМОВ
import * as BABYLON from './core/BabylonBridge.js';
import { Config } from './core/Config.js';
import { BabylonSceneManager } from './core/BabylonScene.js';
import { ObjectManager } from './core/ObjectManager.js';
import { RealtimeSync } from './core/RealtimeSync.js';
import { BabylonToolbar } from './tools/BabylonToolbar.js';

// ========== РЕЖИМ ==========
const MODE = document.body.dataset.mode || 'world';
const ENTITY_ID = document.body.dataset.entityId || null;
console.log(`🎮 COR Editor — режим: ${MODE}${ENTITY_ID ? `, id: ${ENTITY_ID}` : ''}`);

// ========== СЦЕНА ==========
const sm = new BabylonSceneManager();
sm.init();
const scene = sm.scene;

const viewportDiv = document.getElementById('viewport');
if (viewportDiv && sm.canvas) {
    viewportDiv.appendChild(sm.canvas);
    sm.canvas.style.width = '100%';
    sm.canvas.style.height = '100%';
    sm.engine.resize();
}

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
    // Автосохранение при выборе
    if (MODE !== 'world') scheduleEntitySave();
}

function deselectAll() {
    if (selected) {
        if (selected._savedColor) selected.material.albedoColor = selected._savedColor;
        selected = null;
    }
    sm.gizmoManager.attachToMesh(null);
    updateInspectorPanel(null);
}

// ========== ИНСПЕКТОР ==========
function updateInspectorPanel(mesh) {
    const propsDiv = document.getElementById('inspector-props');
    if (!propsDiv) return;

    if (!mesh) {
        propsDiv.innerHTML = '<div class="inspector-section"><div class="inspector-section-title">Ничего не выбрано</div></div>';
        return;
    }

    const meta = mesh.metadata || {};
    const pos = mesh.position;

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

// ========== СТАТУС ==========
function setStatus(text, bg) {
    const el = document.getElementById('info');
    if (!el) return;
    el.textContent = text;
    if (bg) el.style.background = bg;
}

// ========== СОХРАНЕНИЕ (зависит от режима) ==========
let saveTimer = null;

function scheduleEntitySave() {
    if (MODE === 'world') return; // Для мира — через RealtimeSync
    clearTimeout(saveTimer);
    saveTimer = setTimeout(() => saveEntity(), 2000);
}

async function saveEntity() {
    if (!ENTITY_ID) return;

    const children = Object.values(om.allObjects).map((entry) => ({
        name: entry.params?.name || 'object',
        geometry: entry.params?.geometry || 'BoxGeometry',
        color: entry.params?.color || '#ff6600',
        position: [
            +entry.mesh.position.x.toFixed(3),
            +entry.mesh.position.y.toFixed(3),
            +entry.mesh.position.z.toFixed(3)
        ],
        rotation: [
            +entry.mesh.rotation.x.toFixed(3),
            +entry.mesh.rotation.y.toFixed(3),
            +entry.mesh.rotation.z.toFixed(3)
        ],
        scale: [
            +entry.mesh.scaling.x.toFixed(3),
            +entry.mesh.scaling.y.toFixed(3),
            +entry.mesh.scaling.z.toFixed(3)
        ],
        roughness: entry.params?.roughness ?? 0.3,
        metalness: entry.params?.metalness ?? 0.1
    }));

    const payload = {
        name: document.getElementById('entity-name')?.value || 'Без имени',
        description: document.getElementById('entity-desc')?.value || ''
    };

    if (MODE === 'asset') {
        payload.data = { children };
    } else if (MODE === 'tool') {
        payload.default_params = { geometry: 'Group', children };
    }

    const API_URL = MODE === 'asset'
        ? `/api/v1/assets/${ENTITY_ID}/`
        : `/api/v1/tools/${ENTITY_ID}/`;

    try {
        const res = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        setStatus(
            data.status === 'ok' ? '💾 Сохранено' : `❌ ${data.error || res.status}`,
            data.status === 'ok' ? 'rgba(0,150,0,0.75)' : 'rgba(200,0,0,0.75)'
        );
    } catch (err) {
        console.error('Ошибка сохранения:', err);
    }
}

// Ручное сохранение по кнопке
document.getElementById('save-entity-btn')?.addEventListener('click', saveEntity);

// ========== ЗАГРУЗКА СУЩНОСТИ ==========
async function loadEntity() {
    if (!ENTITY_ID || MODE === 'world') return;

    const API_URL = MODE === 'asset'
        ? `/api/v1/assets/${ENTITY_ID}/`
        : `/api/v1/tools/${ENTITY_ID}/`;

    try {
        const res = await fetch(API_URL);
        const data = await res.json();

        document.getElementById('entity-name').value = data.name || '';
        document.getElementById('entity-desc').value = data.description || '';

        // Определяем источник children
        const childrenSource = MODE === 'asset'
            ? (data.data?.children || [])
            : (data.default_params?.children || (data.default_params?.geometry ? [data.default_params] : []));

        childrenSource.forEach((child) => {
            const pos = child.position
                ? new BABYLON.Vector3(child.position[0], child.position[1], child.position[2])
                : new BABYLON.Vector3((Math.random() - 0.5) * 2, 0.5, (Math.random() - 0.5) * 2);
            const mesh = om.createGeometry(
                child.geometry || 'BoxGeometry',
                `Create${(child.geometry || 'BoxGeometry').replace('Geometry', '')}`,
                child,
                null,
                child.color,
                pos
            );
            updateChildrenList();
        });

        setStatus(`📂 ${data.name}`);
    } catch (err) {
        console.error('Ошибка загрузки:', err);
        setStatus('⚠️ Не загружен');
    }
}

function updateChildrenList() {
    const list = document.getElementById('children-list');
    if (!list) return;
    list.innerHTML = '';
    Object.entries(om.allObjects).forEach(([id, entry]) => {
        const div = document.createElement('div');
        div.className = 'child-item' + (selected === entry.mesh ? ' selected' : '');
        div.textContent = `${entry.params?.name || entry.params?.geometry || 'object'}`;
        div.onclick = () => selectMesh(entry.mesh);
        list.appendChild(div);
    });
}

// Переопределяем createGeometry чтобы обновлять список
const originalCreateGeometry = om.createGeometry.bind(om);
om.createGeometry = function (...args) {
    const mesh = originalCreateGeometry(...args);
    updateChildrenList();
    return mesh;
};

// ========== СИНХРОНИЗАЦИЯ (только для мира) ==========
if (MODE === 'world') {
    const sync = new RealtimeSync(om, setStatus, getSelected, deselectAll);
    sync.connect();

    // Тулбар из базы
    const toolbar = new BabylonToolbar(scene, sm, {
        onToolSelected: (tool) => {
            const params = tool.default_params || {};
            const geometry = params.geometry || 'BoxGeometry';

            if (geometry === 'Group' && params.children) {
                const group = new BABYLON.TransformNode(`${tool.name}-${Date.now()}`, scene);
                group.position.set((Math.random() - 0.5) * 4, 0, (Math.random() - 0.5) * 4);
                group.metadata = { id: `${tool.name}-${Date.now()}`, type: 'group', geometry: 'Group', params };
                params.children.forEach(childParams => {
                    const method = `Create${(childParams.geometry || 'BoxGeometry').replace('Geometry', '')}`;
                    const child = BABYLON.MeshBuilder[method](`child_${Date.now()}`, childParams, scene);
                    if (childParams.position) child.position.set(childParams.position[0], childParams.position[1], childParams.position[2]);
                    child.material = new BABYLON.PBRMaterial(`mat_${Date.now()}`, scene);
                    child.material.albedoColor = BABYLON.Color3.FromHexString(childParams.color || '#ff6600');
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

    toolbar.createWithoutGizmo = function () {
        this.gui = BABYLON.GUI.AdvancedDynamicTexture.CreateFullscreenUI('toolbar-ui');
        this._loadFromDatabase();
    };
    toolbar.createWithoutGizmo();
}

// ========== ЗАГРУЗКА ПРИ СТАРТЕ ==========
if (MODE !== 'world') {
    loadEntity();
}

// ========== УДАЛЕНИЕ ==========
document.getElementById('delete-insp-btn')?.addEventListener('click', () => {
    if (!selected) return;
    const id = selected.metadata?.id;
    if (MODE === 'world') {
        // sync.sendDelete(id);
    }
    om.removeObject(id);
    deselectAll();
    updateChildrenList();
    if (MODE !== 'world') scheduleEntitySave();
});

// ========== КЛАВИШИ ==========
window.addEventListener('keydown', e => {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    const k = e.key.toLowerCase();
    const gizmoMap = { w: 'translate', e: 'rotate', r: 'scale' };
    if (gizmoMap[k]) {
        sm.setGizmoMode(gizmoMap[k]);
        highlightGizmoButton(gizmoMap[k]);
    }
    if (k === 'delete' || k === 'backspace') {
        if (selected) {
            om.removeObject(selected.metadata?.id);
            deselectAll();
            updateChildrenList();
            if (MODE !== 'world') scheduleEntitySave();
        }
    }
    if (k === 'escape') deselectAll();
});

function highlightGizmoButton(mode) {
    document.querySelectorAll('#inspector .cor-btn--icon[data-mode]').forEach(b => {
        b.classList.toggle('active', b.dataset.mode === mode);
    });
}

// ========== ИНИЦИАЛИЗАЦИЯ UI ==========
document.querySelectorAll('#inspector .cor-btn--icon[data-mode]').forEach(btn => {
    btn.addEventListener('click', () => {
        highlightGizmoButton(btn.dataset.mode);
        sm.setGizmoMode(btn.dataset.mode);
    });
});

// Сворачивание панелей
document.getElementById('collapse-outliner-btn')?.addEventListener('click', () => {
    const el = document.getElementById('outliner');
    if (el) el.style.display = el.style.display === 'none' ? '' : 'none';
});

document.getElementById('collapse-inspector-btn')?.addEventListener('click', () => {
    const el = document.getElementById('inspector');
    if (el) el.style.display = el.style.display === 'none' ? '' : 'none';
});

// Модалка ролей (только для мира)
if (MODE === 'world') {
    const roleBadge = document.getElementById('role-badge');
    const roleModal = document.getElementById('role-modal');
    if (roleBadge && roleModal) {
        roleBadge.addEventListener('click', () => roleModal.style.display = 'flex');
        roleModal.addEventListener('click', (e) => {
            if (e.target === roleModal) roleModal.style.display = 'none';
        });
    }
    document.getElementById('apply-role-btn')?.addEventListener('click', () => {
        const sel = document.querySelector('#role-modal .modal-option.selected');
        if (sel && roleBadge) {
            const names = { marketer: '📢 Маркетолог', artist: '🎨 Художник', designer: '🏗 Дизайнер', programmer: '💻 Программист' };
            roleBadge.textContent = names[sel.dataset.role] || '🎭 Гость';
            roleModal.style.display = 'none';
        }
    });
    document.querySelectorAll('#role-modal .modal-option').forEach(opt => {
        opt.addEventListener('click', () => {
            document.querySelectorAll('#role-modal .modal-option').forEach(o => o.classList.remove('selected'));
            opt.classList.add('selected');
        });
    });
}

// ========== СТАРТ ==========
setStatus('🎮 COR Ready');
console.log(`🚀 COR Editor запущен (mode: ${MODE})`);