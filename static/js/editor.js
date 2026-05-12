// static/js/editor.js
// ==============================================================================
// COR EDITOR — всё по компонентам, без хардкода
// ==============================================================================

import * as BABYLON from './core/BabylonBridge.js';
import { Config } from './core/Config.js';
import { BabylonSceneManager } from './core/BabylonScene.js';
import { ObjectManager } from './core/ObjectManager.js';
import { RealtimeSync } from './core/RealtimeSync.js';
import { BabylonToolbar } from './tools/BabylonToolbar.js';
import { Inspector } from './tools/Inspector.js';

// ========== СЦЕНА ==========
const sm = new BabylonSceneManager();
sm.init();
const scene = sm.scene;

// ========== МЕНЕДЖЕР ОБЪЕКТОВ ==========
const om = new ObjectManager(scene, sm.shadowGenerator);

// ========== ИНСПЕКТОР ==========
const inspector = new Inspector(scene);
inspector.create();

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
    inspector.attach(mesh);
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
    inspector.detach();
}

// Гизмо — отправка при движении
sm._onGizmoDrag = () => {
    if (selected) {
        sync.sendUpdate(selected);
        sync.scheduleSave();
    }
};

// Инспектор обновляется
setInterval(() => { if (selected) inspector.attach(selected); }, 100);

// ========== СИНХРОНИЗАЦИЯ ==========
const sync = new RealtimeSync(om, setStatus, getSelected, deselectAll);
sync.connect();

// ========== ТУЛБАР ==========
const toolbar = new BabylonToolbar(scene, sm, {
    onToolSelected: (tool) => {
        const params = tool.default_params || {};
        const geometry = params.geometry || 'BoxGeometry';

        if (geometry === 'Group' && params.children) {
            // Составной объект
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
            // Простая геометрия
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

toolbar.create();

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
    if (k === 'w') sm.setGizmoMode('translate');
    if (k === 'e') sm.setGizmoMode('rotate');
    if (k === 'r') sm.setGizmoMode('scale');
    if (k === 'delete' || k === 'backspace') {
        if (selected) { sync.sendDelete(selected.metadata?.id); om.removeObject(selected.metadata?.id); deselectAll(); sync.scheduleSave(); }
    }
    if (k === 'escape') deselectAll();
    if (e.ctrlKey && e.shiftKey && k === 'i') sm.showInspector();
});

// ========== СТАРТ ==========
setStatus('🎮 COR Ready');
console.log('🚀 COR Editor запущен');