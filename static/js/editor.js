// static/js/editor.js
import { WorldView } from './app/WorldView.js';
import { SyncManager } from './app/SyncManager.js';
import { ToolHandler } from './app/ToolHandler.js';

const urlParams = new URLSearchParams(window.location.search);
const CHUNK_ID = urlParams.get('chunk_id') || '4a3f8b2c-1d5e-4f6a-8b9c-0d1e2f3a4b5c';
const WORLD_ID = urlParams.get('world_id') || null;

const API_HOST = window.location.hostname;
const API_BASE = `http://${API_HOST}:8000`;

console.log('🌍 Мир:', WORLD_ID);
console.log('📦 Чанк:', CHUNK_ID);
console.log('🔗 API:', API_BASE);

const infoEl = document.getElementById('info');

function setStatus(text, bg = 'rgba(0, 150, 0, 0.75)') {
    infoEl.textContent = text;
    infoEl.style.background = bg;
}

const world = new WorldView();

let saveTimer = null;

function scheduleSave() {
    if (saveTimer) clearTimeout(saveTimer);
    saveTimer = setTimeout(async () => {
        const objectsData = world.getAllObjectsData();
        const result = await saveToServer(CHUNK_ID, objectsData);
        if (result) {
            setStatus('💾 Сохранено в базу', 'rgba(0, 100, 0, 0.75)');
            setTimeout(() => setStatus('🟢 Подключено', 'rgba(0, 150, 0, 0.75)'), 2000);
        }
    }, 2000);
}

async function saveToServer(chunkId, objectsData) {
    try {
        const body = { objects: objectsData, chunk_type: 'full' };
        if (WORLD_ID) body.world_id = WORLD_ID;
        const response = await fetch(`${API_BASE}/api/chunk/${chunkId}/save/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        const result = await response.json();
        console.log('💾 Чанк сохранён:', result);
        return result;
    } catch (error) {
        console.error('❌ Ошибка сохранения:', error);
        return null;
    }
}

async function loadFromServer(chunkId) {
    try {
        const response = await fetch(`${API_BASE}/api/chunk/${chunkId}/load/`);
        const data = await response.json();
        console.log('📂 Чанк загружен:', data);
        return data;
    } catch (error) {
        console.error('❌ Ошибка загрузки:', error);
        return { objects: {}, chunk_type: 'void' };
    }
}

const sync = new SyncManager(
    `ws://${API_HOST}:8000/ws/chunk/${CHUNK_ID}/`,
    {
        onWelcome: async (data) => {
            const saved = await loadFromServer(CHUNK_ID);
            if (saved.objects && Object.keys(saved.objects).length > 0) {
                world.loadFromServerData(saved.objects);
                setStatus('📂 Загружено из базы', 'rgba(0, 100, 0, 0.75)');
            } else if (data.objects && Object.keys(data.objects).length > 0) {
                world.loadFromServerData(data.objects);
            }
            setTimeout(() => setStatus('🟢 Подключено', 'rgba(0, 150, 0, 0.75)'), 2000);
        },

        onServerIdReceived: (clientId, serverId) => {
            const entry = world.allObjects[clientId];
            if (entry && entry.mesh) {
                entry.mesh.userData.serverId = serverId;
            }
        },

        onObjectDeleted: (objectId) => {
            // Проверяем и по server_id, и по client_id
            const entry = world.allObjects[objectId];
            if (entry) {
                world.sceneManager.remove(entry.mesh);
                world.dragManager.removeDraggable(entry.mesh);
                delete world.allObjects[objectId];
                if (world.selectedObject === entry.mesh) {
                    world.deselectAll();
                }
            }
        },

        onObjectUpdated: (data, params) => {
            const objId = data.server_id || data.object_id || data.cube_id;
            world.updateOrCreateObject(
                objId, params, data.position,
                data.rotation || null,
                data.scale || null
            );
            scheduleSave();
        },

        onStatusChange: setStatus,
    }
);

world.onObjectDragged = (object) => {
    sync.sendObjectUpdate(object);
    scheduleSave();
};

sync.connect();

const tools = new ToolHandler(
    (params) => world.createObject(params),
    (object, params) => {
        sync.sendObjectCreate(object, params);
        scheduleSave();
    },
    setStatus
);
tools.load(WORLD_ID);

console.log('COR Editor initialized');

window.addEventListener('keydown', (event) => {
    if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') return;
    switch (event.key.toLowerCase()) {
        case 'w': document.querySelector('.gizmo-btn[data-mode="translate"]')?.click(); break;
        case 'e': document.querySelector('.gizmo-btn[data-mode="rotate"]')?.click(); break;
        case 'r': document.querySelector('.gizmo-btn[data-mode="scale"]')?.click(); break;
        case 'delete': case 'backspace': document.getElementById('delete-btn')?.click(); break;
        case 'escape': world.deselectAll(); setStatus('🟢 Подключено', 'rgba(0, 150, 0, 0.75)'); break;
    }
});

document.querySelectorAll('.gizmo-btn[data-mode]').forEach(btn => {
    btn.addEventListener('click', () => {
        const mode = btn.dataset.mode;
        world.setGizmoMode(mode);
        document.querySelectorAll('.gizmo-btn[data-mode]').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const modeNames = { translate: 'Перемещение', rotate: 'Вращение', scale: 'Масштаб' };
        setStatus(`🔧 ${modeNames[mode]}`, 'rgba(100, 50, 0, 0.85)');
        setTimeout(() => setStatus('🟢 Подключено'), 2000);
    });
});

document.getElementById('delete-btn').addEventListener('click', () => {
    if (world.selectedObject) {
        const obj = world.selectedObject;
        const objId = obj.userData.id;
        sync.sendObjectDelete(objId);
        world.sceneManager.remove(obj);
        world.dragManager.removeDraggable(obj);
        delete world.allObjects[objId];
        world.deselectAll();
        scheduleSave();
        setStatus('🗑 Объект удалён', 'rgba(200, 0, 0, 0.75)');
        setTimeout(() => setStatus('🟢 Подключено'), 2000);
    }
});