// static/js/editor_core.js
// ==============================================================================
// УНИВЕРСАЛЬНЫЙ 3D-РЕДАКТОР — Ассеты, Инструменты, Сцены
// ==============================================================================

import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { TransformControls } from 'three/addons/controls/TransformControls.js';
import { createMeshFromParams } from './objects/MeshFactory.js';
import { Toolbar } from './tools/toolbar.js';

// ==============================================================================
// 1. КОНФИГУРАЦИЯ
// ==============================================================================

const parts = window.location.pathname.split('/').filter(Boolean);
const ENTITY_ID = parts[parts.length - 1];
const MODE = parts.includes('asset') ? 'asset' : parts.includes('tool') ? 'tool' : 'scene';

const API_MAP = {
    asset: `/api/v1/assets/${ENTITY_ID}/`,
    tool: `/api/v1/tools/${ENTITY_ID}/`,
    scene: `/api/v1/scenes/${ENTITY_ID}/`,
};
const API_URL = API_MAP[MODE] || API_MAP.asset;
const LABEL = { asset: 'Ассет', tool: 'Инструмент', scene: 'Сцена' }[MODE];

console.log(`📦 Редактор: ${LABEL} | 🆔 ${ENTITY_ID} | 🔗 ${API_URL}`);

// ==============================================================================
// 2. СЦЕНА (универсальный конструктор)
// ==============================================================================

function createEditorScene() {
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x2a2a3e);
    scene.fog = new THREE.Fog(0x2a2a3e, 20, 60);

    const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.set(5, 8, 10);
    camera.lookAt(0, 0, 0);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFShadowMap;
    document.body.appendChild(renderer.domElement);

    // Свет
    scene.add(new THREE.AmbientLight(0x404060, 2.5));
    const dirLight = new THREE.DirectionalLight(0xffffff, 4);
    dirLight.position.set(5, 10, 5);
    dirLight.castShadow = true;
    dirLight.shadow.mapSize.set(1024, 1024);
    scene.add(dirLight);

    // Пол
    const floor = new THREE.Mesh(new THREE.PlaneGeometry(20, 20), new THREE.ShadowMaterial({ opacity: 0.3 }));
    floor.rotation.x = -Math.PI / 2;
    floor.receiveShadow = true;
    scene.add(floor);

    // Сетка
    scene.add(new THREE.GridHelper(20, 20, 0x444466, 0x222244));

    // OrbitControls
    const orbit = new OrbitControls(camera, renderer.domElement);
    orbit.enableDamping = true;
    orbit.dampingFactor = 0.08;
    orbit.target.set(0, 0.5, 0);

    // TransformControls
    const gizmo = new TransformControls(camera, renderer.domElement);
    gizmo.setMode('translate');
    gizmo.setSize(0.8);
    gizmo.addEventListener('dragging-changed', e => { orbit.enabled = !e.value; });
    scene.add(gizmo);

    return { scene, camera, renderer, orbit, gizmo };
}

const { scene, camera, renderer, orbit, gizmo } = createEditorScene();

// ==============================================================================
// 3. ДАННЫЕ
// ==============================================================================

let allObjects = {};
let selectedObject = null;
let isUngrouped = false;

// ==============================================================================
// 4. РАБОТА С ОБЪЕКТАМИ
// ==============================================================================

/**
 * Создаёт 3D-объект и сохраняет ВСЕ параметры в allObjects
 */
function addChild(params, pos = null, rot = null, scl = null) {
    const obj = createMeshFromParams(params, pos);
    if (rot) obj.rotation.set(rot.x || 0, rot.y || 0, rot.z || 0);
    if (scl) obj.scale.set(scl.x || 1, scl.y || 1, scl.z || 1);
    scene.add(obj);

    // Сохраняем ПОЛНЫЕ параметры, включая width/height/radiusTop и т.д.
    allObjects[obj.uuid] = {
        mesh: obj,
        data: {
            ...params,
            position: pos ? [pos.x, pos.y, pos.z] : [obj.position.x, obj.position.y, obj.position.z],
            rotation: rot ? [rot.x || 0, rot.y || 0, rot.z || 0] : [obj.rotation.x, obj.rotation.y, obj.rotation.z],
            scale: scl ? [scl.x || 1, scl.y || 1, scl.z || 1] : [obj.scale.x, obj.scale.y, obj.scale.z]
        }
    };
    return obj;
}

/**
 * Рекурсивно загружает children из JSON
 */
function loadChildren(children, parentPos = { x: 0, y: 0, z: 0 }) {
    if (!Array.isArray(children)) return;
    children.forEach(c => {
        const pos = c.position
            ? { x: c.position[0] + parentPos.x, y: c.position[1] + parentPos.y, z: c.position[2] + parentPos.z }
            : { ...parentPos };
        const rot = c.rotation ? { x: c.rotation[0] || 0, y: c.rotation[1] || 0, z: c.rotation[2] || 0 } : null;
        const scl = c.scale_override || c.scale
            ? {
                x: (c.scale_override || c.scale || [1, 1, 1])[0],
                y: (c.scale_override || c.scale || [1, 1, 1])[1],
                z: (c.scale_override || c.scale || [1, 1, 1])[2]
            }
            : null;

        if (c.geometry === 'Group' || c.children) {
            isUngrouped = true;
            loadChildren(c.children || [], pos);
        } else {
            // Передаём ВСЕ поля объекта — width, height, radiusTop и т.д.
            addChild(c, pos, rot, scl);
        }
    });
}

/**
 * Список всех геометрических параметров, которые нужно сохранять
 */
const GEOMETRY_PARAMS = [
    'width', 'height', 'depth', 'size',
    'radius', 'radiusTop', 'radiusBottom',
    'tube', 'innerRadius', 'outerRadius',
    'length',
    'segments', 'widthSegments', 'heightSegments',
    'radialSegments', 'tubularSegments',
    'p', 'q', 'arc',
    'profile', 'extrudeDepth',
    'bevelThickness', 'bevelSize', 'bevelSegments',
    'wireframe', 'opacity', 'transparent',
    'emissive', 'roughness', 'metalness',
    'defaultY'
];

/**
 * Собирает все объекты в формат JSON для сохранения
 */
function collectChildren() {
    return Object.values(allObjects)
        .filter(e => e.mesh)
        .map(e => {
            const child = {
                name: e.data.name || 'object',
                geometry: e.data.geometry || 'BoxGeometry',
                color: e.data.color || '#ff6600',
                position: [
                    round(e.mesh.position.x),
                    round(e.mesh.position.y),
                    round(e.mesh.position.z)
                ],
                rotation: [
                    round(e.mesh.rotation.x),
                    round(e.mesh.rotation.y),
                    round(e.mesh.rotation.z)
                ],
                scale: [
                    round(e.mesh.scale.x),
                    round(e.mesh.scale.y),
                    round(e.mesh.scale.z)
                ],
                material: {
                    roughness: e.data.roughness ?? 0.3,
                    metalness: e.data.metalness ?? 0.1
                }
            };

            // Сохраняем ВСЕ геометрические параметры
            for (const key of GEOMETRY_PARAMS) {
                if (e.data[key] !== undefined) {
                    child[key] = e.data[key];
                }
            }

            return child;
        })
        .sort((a, b) => a.position[1] - b.position[1]);
}

function round(v) { return +v.toFixed(3); }

// ==============================================================================
// 5. ВЫДЕЛЕНИЕ
// ==============================================================================

const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();

function select(obj) {
    if (selectedObject === obj) return;
    if (selectedObject) highlight(selectedObject, false);
    selectedObject = obj;
    gizmo.attach(obj);
    highlight(obj, true);
    updateUI();
}

function deselect() {
    if (selectedObject) highlight(selectedObject, false);
    selectedObject = null;
    gizmo.detach();
    updateUI();
}

function highlight(obj, on) {
    obj.traverse(c => { if (c.material?.emissive) c.material.emissive.set(on ? 0x331100 : 0); });
}

renderer.domElement.addEventListener('click', e => {
    mouse.set((e.clientX / innerWidth) * 2 - 1, -(e.clientY / innerHeight) * 2 + 1);
    raycaster.setFromCamera(mouse, camera);
    const targets = Object.values(allObjects).map(o => o.mesh);
    const hits = raycaster.intersectObjects(targets, true);
    if (hits.length) {
        let obj = hits[0].object;
        while (obj && !allObjects[obj.uuid]) obj = obj.parent;
        if (obj && allObjects[obj.uuid]) { select(obj); return; }
    }
    deselect();
});

// ==============================================================================
// 6. UI
// ==============================================================================

function updateUI() {
    const list = document.getElementById('children-list');
    if (!list) return;
    list.innerHTML = '';
    Object.entries(allObjects).forEach(([uuid, e]) => {
        if (!e.mesh) return;
        const div = document.createElement('div');
        div.className = 'child-item' + (selectedObject === e.mesh ? ' selected' : '');
        div.textContent = `${e.data.name || e.data.geometry} (${e.data.geometry || '?'})`;
        div.onclick = () => select(e.mesh);
        list.appendChild(div);
    });
    updateInspector();
}

function updateInspector() {
    const panel = document.getElementById('inspector-panel');
    if (!panel) return;
    if (!selectedObject) { panel.style.display = 'none'; return; }
    panel.style.display = 'block';
    const o = selectedObject;
    panel.querySelector('.inspector-pos-x').value = round(o.position.x);
    panel.querySelector('.inspector-pos-y').value = round(o.position.y);
    panel.querySelector('.inspector-pos-z').value = round(o.position.z);
    panel.querySelector('.inspector-rot-x').value = round(THREE.MathUtils.radToDeg(o.rotation.x));
    panel.querySelector('.inspector-rot-y').value = round(THREE.MathUtils.radToDeg(o.rotation.y));
    panel.querySelector('.inspector-rot-z').value = round(THREE.MathUtils.radToDeg(o.rotation.z));
    panel.querySelector('.inspector-scale-x').value = round(o.scale.x);
    panel.querySelector('.inspector-scale-y').value = round(o.scale.y);
    panel.querySelector('.inspector-scale-z').value = round(o.scale.z);
}

// Связываем инспектор
['x', 'y', 'z'].forEach(a => {
    ['pos', 'rot', 'scale'].forEach(t => {
        const input = document.querySelector(`.inspector-${t}-${a}`);
        if (!input) return;
        input.addEventListener('input', () => {
            if (!selectedObject) return;
            const v = parseFloat(input.value) || 0;
            if (t === 'pos') selectedObject.position[a] = v;
            if (t === 'rot') selectedObject.rotation[a] = THREE.MathUtils.degToRad(v);
            if (t === 'scale') selectedObject.scale[a] = v || 1;
            updateUI();
        });
    });
});

// ==============================================================================
// 7. API
// ==============================================================================

async function save() {
    const children = collectChildren();
    const payload = {
        name: document.getElementById('entity-name')?.value || 'Без имени',
        description: document.getElementById('entity-desc')?.value || '',
    };

    if (MODE === 'asset') {
        payload.data = { children };
        payload.animation = {};
        payload.tags = [];
    } else if (MODE === 'tool') {
        payload.default_params = { geometry: 'Group', children, defaultY: 0 };
    }

    const info = document.getElementById('info');
    try {
        const res = await fetch(API_URL, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
        const data = await res.json();
        if (info) {
            info.textContent = data.status === 'ok' ? '💾 Сохранено!' : `❌ ${data.error || res.status}`;
            info.style.background = data.status === 'ok' ? 'rgba(0,150,0,0.75)' : 'rgba(200,0,0,0.75)';
            setTimeout(() => { info.textContent = `🎨 ${LABEL}`; info.style.background = 'rgba(0,0,0,0.75)'; }, 2000);
        }
    } catch (err) {
        console.error(err);
        if (info) { info.textContent = '❌ Ошибка'; info.style.background = 'rgba(200,0,0,0.75)'; }
    }
}

async function load() {
    try {
        const res = await fetch(API_URL);
        if (!res.ok) throw new Error(res.status);
        const data = await res.json();

        document.getElementById('entity-name').value = data.name || '';
        document.getElementById('entity-desc').value = data.description || '';

        // Очистка
        Object.values(allObjects).forEach(e => scene.remove(e.mesh));
        allObjects = {};
        isUngrouped = false;

        // ===== ЗАГРУЗКА С УЧЁТОМ ТИПА СУЩНОСТИ =====
        if (MODE === 'asset') {
            loadChildren(data.data?.children || []);
        } else if (MODE === 'tool') {
            const params = data.default_params || {};
            if (params.geometry === 'Group' && params.children) {
                loadChildren(params.children);
            } else if (params.geometry) {
                // Простой инструмент — один объект
                addChild(params, { x: 0, y: params.defaultY || 0.5, z: 0 });
            }
        }

        updateUI();
        document.getElementById('info').textContent = `📂 ${LABEL}: ${data.name}`;
    } catch (err) {
        console.error(err);
        document.getElementById('info').textContent = `⚠️ Не загружен`;
    }
}

// ==============================================================================
// 8. ТУЛБАР
// ==============================================================================

new Toolbar('#toolbar', tool => {
    if (tool.tool_type !== 'create_mesh') return;
    const params = tool.default_params || {};
    if (params.geometry === 'Group' && params.children) {
        const base = { x: (Math.random() - 0.5) * 4, y: params.defaultY || 0, z: (Math.random() - 0.5) * 4 };
        params.children.forEach(c => {
            const pos = c.position
                ? { x: c.position[0] + base.x, y: c.position[1] + base.y, z: c.position[2] + base.z }
                : { ...base };
            addChild({ ...c, geometry: c.geometry || 'BoxGeometry' }, pos);
        });
        isUngrouped = true;
    } else {
        addChild(params);
    }
}).loadTools();

// ==============================================================================
// 9. КНОПКИ
// ==============================================================================

document.getElementById('save-btn')?.addEventListener('click', save);

document.getElementById('delete-btn')?.addEventListener('click', () => {
    if (!selectedObject) return;
    scene.remove(selectedObject);
    delete allObjects[selectedObject.uuid];
    deselect();
    updateUI();
});

document.getElementById('ungroup-btn')?.addEventListener('click', () => {
    if (!selectedObject) return;
    const children = selectedObject.userData.params?.children;
    if (!children?.length) return;
    const pos = selectedObject.position.clone();
    children.forEach(c => {
        const cp = c.position
            ? { x: c.position[0] + pos.x, y: c.position[1] + pos.y, z: c.position[2] + pos.z }
            : { x: pos.x, y: pos.y, z: pos.z };
        addChild({ ...c, geometry: c.geometry || 'BoxGeometry' }, cp);
    });
    scene.remove(selectedObject);
    delete allObjects[selectedObject.uuid];
    deselect();
    isUngrouped = true;
    updateUI();
});

document.querySelectorAll('.gizmo-btn[data-mode]').forEach(b => {
    b.addEventListener('click', () => {
        gizmo.setMode(b.dataset.mode);
        document.querySelectorAll('.gizmo-btn[data-mode]').forEach(x => x.classList.remove('active'));
        b.classList.add('active');
    });
});

// Клавиши
window.addEventListener('keydown', e => {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    const map = { w: 'translate', e: 'rotate', r: 'scale' };
    if (map[e.key]) document.querySelector(`.gizmo-btn[data-mode="${map[e.key]}"]`)?.click();
    if (e.key === 'Delete' || e.key === 'Backspace') document.getElementById('delete-btn')?.click();
    if (e.key === 'Escape') deselect();
});

// Ресайз
window.addEventListener('resize', () => {
    camera.aspect = innerWidth / innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(innerWidth, innerHeight);
});

// Анимация
(function animate() {
    requestAnimationFrame(animate);
    orbit.update();
    renderer.render(scene, camera);
})();

// ==============================================================================
// 10. СТАРТ
// ==============================================================================

console.log(`🎨 Редактор ${LABEL} запущен`);
load();