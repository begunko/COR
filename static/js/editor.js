import { SceneManager } from './core/Scene.js';
import { WebSocketClient } from './core/WebSocketClient.js';
import { createMeshFromParams } from './objects/MeshFactory.js';
import { createCursor } from './objects/Cursor.js';
import { DragManager } from './controls/DragManager.js';
import { Toolbar } from './tools/Toolbar.js';

// ============ DOM ============
const infoEl = document.getElementById('info');

function setStatus(text, bg = 'rgba(0, 150, 0, 0.75)') {
    infoEl.textContent = text;
    infoEl.style.background = bg;
}

// ============ Сцена ============
const sceneManager = new SceneManager();
sceneManager.init();

// ============ Состояние ============
let myUserId = null;
let myColor = null;
const remoteCursors = {};   // { userId: THREE.Mesh }
const allCubes = {};        // { cubeId: THREE.Mesh }

// ============ DragManager ============
const dragManager = new DragManager(sceneManager, (object) => {
    // Отправляем позицию при перетаскивании
    wsClient.send({
        type: 'cube_move',
        cube_id: object.userData.id,
        color: object.userData.color,
        position: {
            x: +object.position.x.toFixed(3),
            y: +object.position.y.toFixed(3),
            z: +object.position.z.toFixed(3),
        },
    });
});
dragManager.init();

// ============ Панель инструментов ============
function onToolSelected(tool) {
    setStatus(`🔧 Инструмент: ${tool.display_name}`, 'rgba(100, 50, 0, 0.85)');

    if (tool.tool_type === 'create_mesh') {
        const params = tool.default_params || {};
        const newObject = createMeshFromParams(params);

        sceneManager.add(newObject);
        allCubes[newObject.userData.id] = newObject;
        dragManager.addDraggable(newObject);

        // Отправляем на сервер
        wsClient.send({
            type: 'object_create',
            object_id: newObject.userData.id,
            object_type: newObject.userData.type,
            color: newObject.userData.color,
            params: params,
            position: {
                x: +newObject.position.x.toFixed(3),
                y: +newObject.position.y.toFixed(3),
                z: +newObject.position.z.toFixed(3),
            },
        });
    }

    setTimeout(() => setStatus('🟢 Подключено'), 2000);
}

const toolbar = new Toolbar('#toolbar', onToolSelected);
toolbar.loadTools();

// ============ WebSocket ============
const wsClient = new WebSocketClient(
    `ws://127.0.0.1:8000/ws/chunk/test-chunk-001/`,
    {
        onOpen: () => setStatus('🟢 Подключено'),

        onMessage: (data) => {
            if (data.type === 'welcome') {
                myUserId = data.user_id;
                myColor = data.color;

                // Мой курсор
                const myCursor = createCursor(myColor);
                sceneManager.add(myCursor);
                remoteCursors[myUserId] = myCursor;

                // Существующие кубы
                if (data.cubes) {
                    for (const [cubeId, cubeData] of Object.entries(data.cubes)) {
                        const cube = createCube(cubeData.color, cubeData.position);
                        cube.userData.id = cubeId;
                        sceneManager.add(cube);
                        allCubes[cubeId] = cube;
                        dragManager.addDraggable(cube);
                    }
                }

                // Чужие курсоры
                if (data.cursors) {
                    for (const [userId, cursorData] of Object.entries(data.cursors)) {
                        if (userId !== myUserId) {
                            const cursor = createCursor(cursorData.color);
                            cursor.position.set(
                                cursorData.position.x,
                                cursorData.position.y,
                                cursorData.position.z
                            );
                            sceneManager.add(cursor);
                            remoteCursors[userId] = cursor;
                        }
                    }
                }
            }

            // Объект создан/обновлён
            if ((data.type === 'cube_moved' || data.type === 'object_create' || data.type === 'object_updated')
                && data.user_id !== myUserId) {

                if (!allCubes[data.object_id || data.cube_id]) {
                    const params = data.params || {};
                    const color = data.color || '#ff6600';
                    const newObj = createMeshFromParams({ ...params, color }, data.position);
                    newObj.userData.id = data.object_id || data.cube_id;
                    sceneManager.add(newObj);
                    allCubes[newObj.userData.id] = newObj;
                    dragManager.addDraggable(newObj);
                } else {
                    allCubes[data.object_id || data.cube_id].position.set(
                        data.position.x, data.position.y, data.position.z
                    );
                }
                setStatus(`🔄 Объект передвинут: ${data.user_id}`, 'rgba(0, 100, 200, 0.75)');
                setTimeout(() => setStatus('🟢 Подключено'), 2000);
            }

            // Курсор передвинут
            if (data.type === 'cursor_moved' && data.user_id !== myUserId) {
                if (!remoteCursors[data.user_id]) {
                    const cursor = createCursor(data.color);
                    sceneManager.add(cursor);
                    remoteCursors[data.user_id] = cursor;
                }
                remoteCursors[data.user_id].position.set(
                    data.position.x, data.position.y, data.position.z
                );
            }

            // Пользователь ушёл
            if (data.type === 'user_left') {
                if (remoteCursors[data.user_id]) {
                    sceneManager.remove(remoteCursors[data.user_id]);
                    delete remoteCursors[data.user_id];
                }
            }
        },

        onClose: () => setStatus('🔴 Соединение потеряно', 'rgba(200, 0, 0, 0.75)'),
        onError: () => setStatus('⚠️ Ошибка WebSocket', 'rgba(200, 100, 0, 0.75)'),
    }
);
wsClient.connect();

// ============ Отслеживание мыши для курсора ============
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();
const plane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);

window.addEventListener('mousemove', (event) => {
    mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
    mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

    raycaster.setFromCamera(mouse, sceneManager.camera);
    const intersection = new THREE.Vector3();
    raycaster.ray.intersectPlane(plane, intersection);

    if (intersection && wsClient.isConnected()) {
        wsClient.send({
            type: 'cursor_move',
            position: {
                x: +intersection.x.toFixed(3),
                y: +intersection.y.toFixed(3),
                z: +intersection.z.toFixed(3),
            },
        });
    }
});

console.log('COR Editor initialized');