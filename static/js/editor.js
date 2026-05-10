// static/js/editor.js
import { WorldView } from './app/WorldView.js';
import { SyncManager } from './app/SyncManager.js';
import { ToolHandler } from './app/ToolHandler.js';

// ============ Конфигурация ============
// Читаем параметры из URL (передаются из админки)
const urlParams = new URLSearchParams(window.location.search);
const CHUNK_ID = urlParams.get('chunk_id') || '4a3f8b2c-1d5e-4f6a-8b9c-0d1e2f3a4b5c';
const WORLD_ID = urlParams.get('world_id') || null;

// Отображаем, в каком мире мы находимся
if (WORLD_ID) {
    console.log('🌍 Мир:', WORLD_ID);
    console.log('📦 Чанк:', CHUNK_ID);
}

// ============ DOM ============
const infoEl = document.getElementById('info');

function setStatus(text, bg = 'rgba(0, 150, 0, 0.75)') {
    infoEl.textContent = text;
    infoEl.style.background = bg;
}

// ============ Мир (сцена + объекты + drag) ============
const world = new WorldView();

// ============ Автосохранение ============
let saveTimer = null;

function scheduleSave() {
    // Отложенное сохранение через 2 секунды после последнего изменения
    if (saveTimer) clearTimeout(saveTimer);
    saveTimer = setTimeout(() => {
        const objectsData = world.getAllObjectsData();
        sync.saveToServer(CHUNK_ID, objectsData);
        setStatus('💾 Сохранено в базу', 'rgba(0, 100, 0, 0.75)');
        setTimeout(() => setStatus('🟢 Подключено', 'rgba(0, 150, 0, 0.75)'), 2000);
    }, 2000);
}

// ============ Синхронизация (WebSocket) ============
const sync = new SyncManager(
    `ws://192.168.1.41:8000/ws/chunk/${CHUNK_ID}/`,
    {
        onWelcome: async (data) => {
            // Сначала пробуем загрузить из базы
            const saved = await sync.loadFromServer(CHUNK_ID);

            if (saved.objects && Object.keys(saved.objects).length > 0) {
                // Загружаем сохранённые объекты
                world.loadFromServerData(saved.objects);
                setStatus('📂 Загружено из базы', 'rgba(0, 100, 0, 0.75)');
            } else if (data.cubes && Object.keys(data.cubes).length > 0) {
                // Если в базе пусто — берём из памяти сервера
                world.loadFromServerData(data.cubes);
            }

            setTimeout(() => setStatus('🟢 Подключено', 'rgba(0, 150, 0, 0.75)'), 2000);
        },

        onObjectDeleted: (objectId) => {
            if (world.allObjects[objectId]) {
                const obj = world.allObjects[objectId].mesh;
                world.sceneManager.remove(obj);
                world.dragManager.removeDraggable(obj);
                delete world.allObjects[objectId];
                if (world.selectedObject === obj) {
                    world.deselectAll();
                }
            }
        },

        onObjectUpdated: (data, params) => {
            const objId = data.object_id || data.cube_id;
            world.updateOrCreateObject(
                objId, params, data.position,
                data.rotation || null,
                data.scale || null
            );
            scheduleSave();  // Сохраняем при каждом изменении
        },

        onStatusChange: setStatus,
    }
);

// При перетаскивании объекта — отправляем через WebSocket и сохраняем
world.onObjectDragged = (object) => {
    sync.sendObjectUpdate(object);
    scheduleSave();
};

sync.connect();

// ============ Инструменты ============
const tools = new ToolHandler(
    // Создать объект в мире
    (params) => world.createObject(params),

    // После создания — отправить на сервер (WebSocket + сохранение)
    (object, params) => {
        sync.sendObjectCreate(object, params);
        scheduleSave();
    },

    // Обновление статуса
    setStatus
);
tools.load();

console.log('COR Editor initialized with database persistence');

window.addEventListener('keydown', (event) => {
    if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') return;

    switch (event.key.toLowerCase()) {
        case 'w':
            document.querySelector('.gizmo-btn[data-mode="translate"]')?.click();
            break;
        case 'e':
            document.querySelector('.gizmo-btn[data-mode="rotate"]')?.click();
            break;
        case 'r':
            document.querySelector('.gizmo-btn[data-mode="scale"]')?.click();
            break;
        case 'delete':
        case 'backspace':
            document.getElementById('delete-btn')?.click();
            break;
        case 'escape':
            world.deselectAll();
            setStatus('🟢 Подключено', 'rgba(0, 150, 0, 0.75)');
            break;
    }
});

// ============ Кнопки гизмо ============
document.querySelectorAll('.gizmo-btn[data-mode]').forEach(btn => {
    btn.addEventListener('click', () => {
        const mode = btn.dataset.mode;
        world.setGizmoMode(mode);

        // Подсветка активной кнопки
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
        // Отправляем удаление на сервер
        sync.sendObjectDelete(objId);
        // Удаляем из сцены
        world.sceneManager.remove(obj);
        world.dragManager.removeDraggable(obj);
        delete world.allObjects[objId];
        world.deselectAll();
        // Сохраняем изменения в базу
        scheduleSave();
        setStatus('🗑 Объект удалён', 'rgba(200, 0, 0, 0.75)');
        setTimeout(() => setStatus('🟢 Подключено'), 2000);
    }
});
