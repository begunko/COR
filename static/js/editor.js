import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { DragControls } from 'three/addons/controls/DragControls.js';

// ============ DOM ============
const infoEl = document.getElementById('info');

// ============ Сцена ============
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x1a1a2e);

const grid = new THREE.GridHelper(20, 20, 0x444466, 0x222244);
scene.add(grid);

// ============ Камера ============
const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.set(5, 8, 10);
camera.lookAt(0, 0, 0);

// ============ Рендерер ============
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

// ============ OrbitControls ============
const orbitControls = new OrbitControls(camera, renderer.domElement);
orbitControls.enableDamping = true;
orbitControls.dampingFactor = 0.08;
orbitControls.target.set(0, 0.5, 0);

// ============ Освещение ============
const ambientLight = new THREE.AmbientLight(0x404060, 2.5);
scene.add(ambientLight);

const dirLight = new THREE.DirectionalLight(0xffffff, 4);
dirLight.position.set(5, 10, 5);
dirLight.castShadow = true;
dirLight.shadow.mapSize.width = 1024;
dirLight.shadow.mapSize.height = 1024;
dirLight.shadow.camera.near = 0.5;
dirLight.shadow.camera.far = 50;
scene.add(dirLight);

const floor = new THREE.Mesh(
    new THREE.PlaneGeometry(20, 20),
    new THREE.ShadowMaterial({ opacity: 0.3 })
);
floor.rotation.x = -Math.PI / 2;
floor.receiveShadow = true;
scene.add(floor);

// ============ Пользователи и кубы ============
const USER_COLORS = [
    '#ff6600', '#00cc44', '#3388ff', '#ff3377',
    '#ffcc00', '#33cccc', '#cc33ff', '#ff8833'
];

let myUserId = null;
let myColor = null;
const remoteCursors = {};   // { userId: THREE.Mesh }
const remoteCubes = {};     // { cubeId: THREE.Mesh }
const allDraggable = [];    // все кубы, которые можно таскать

// ============ Создание куба ============
function createCube(id, color, position = null) {
    const geometry = new THREE.BoxGeometry(1, 1, 1);
    const material = new THREE.MeshStandardMaterial({
        color: color,
        roughness: 0.3,
        metalness: 0.1,
    });
    const cube = new THREE.Mesh(geometry, material);
    cube.castShadow = true;
    cube.receiveShadow = true;
    cube.userData = { id: id, color: color };

    if (position) {
        cube.position.set(position.x, position.y, position.z);
    } else {
        cube.position.set(
            (Math.random() - 0.5) * 6,
            0.5,
            (Math.random() - 0.5) * 6
        );
    }

    scene.add(cube);
    allDraggable.push(cube);
    return cube;
}

// ============ Курсор пользователя ============
function createCursor(color) {
    const geometry = new THREE.SphereGeometry(0.15, 16, 16);
    const material = new THREE.MeshBasicMaterial({ color: color });
    const cursor = new THREE.Mesh(geometry, material);
    cursor.position.set(0, -10, 0); // прячем под пол
    scene.add(cursor);
    return cursor;
}

// ============ DragControls ============
const dragControls = new DragControls(allDraggable, camera, renderer.domElement);

dragControls.addEventListener('dragstart', (event) => {
    orbitControls.enabled = false;
    event.object.material.emissive = new THREE.Color(0x331100);
});

dragControls.addEventListener('drag', (event) => {
    sendCubePosition(event.object);
});

dragControls.addEventListener('dragend', (event) => {
    orbitControls.enabled = true;
    event.object.material.emissive = new THREE.Color(0x000000);
});

// ============ WebSocket ============
const CHUNK_ID = 'test-chunk-001';
let ws = null;

function connectWebSocket() {
    ws = new WebSocket(`ws://127.0.0.1:8000/ws/chunk/${CHUNK_ID}/`);

    ws.onopen = () => {
        infoEl.textContent = '🟢 Подключено';
        infoEl.style.background = 'rgba(0, 150, 0, 0.75)';
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.type === 'welcome') {
            // Сервер прислал наш ID и цвет
            myUserId = data.user_id;
            myColor = data.color;

            // Создаём существующие кубы
            if (data.cubes) {
                for (const [cubeId, cubeData] of Object.entries(data.cubes)) {
                    remoteCubes[cubeId] = createCube(cubeId, cubeData.color, cubeData.position);
                }
            }

            // Создаём курсоры существующих пользователей
            if (data.cursors) {
                for (const [userId, cursorData] of Object.entries(data.cursors)) {
                    if (userId !== myUserId) {
                        remoteCursors[userId] = createCursor(cursorData.color);
                        remoteCursors[userId].position.set(
                            cursorData.position.x,
                            cursorData.position.y,
                            cursorData.position.z
                        );
                    }
                }
            }

            // Мой курсор
            remoteCursors[myUserId] = createCursor(myColor);
        }

        if (data.type === 'cube_moved') {
            if (!remoteCubes[data.cube_id]) {
                remoteCubes[data.cube_id] = createCube(data.cube_id, data.color, data.position);
            } else {
                remoteCubes[data.cube_id].position.set(
                    data.position.x, data.position.y, data.position.z
                );
            }
            infoEl.textContent = `🔄 Куб передвинут: ${data.user_id}`;
            infoEl.style.background = 'rgba(0, 100, 200, 0.75)';
            setTimeout(() => {
                infoEl.textContent = '🟢 Подключено';
                infoEl.style.background = 'rgba(0, 150, 0, 0.75)';
            }, 2000);
        }

        if (data.type === 'cursor_moved') {
            if (data.user_id !== myUserId) {
                if (!remoteCursors[data.user_id]) {
                    remoteCursors[data.user_id] = createCursor(data.color);
                }
                remoteCursors[data.user_id].position.set(
                    data.position.x, data.position.y, data.position.z
                );
            }
        }

        if (data.type === 'user_left') {
            if (remoteCursors[data.user_id]) {
                scene.remove(remoteCursors[data.user_id]);
                delete remoteCursors[data.user_id];
            }
        }
    };

    ws.onclose = () => {
        infoEl.textContent = '🔴 Соединение потеряно. Переподключение...';
        infoEl.style.background = 'rgba(200, 0, 0, 0.75)';
        setTimeout(connectWebSocket, 2000);
    };

    ws.onerror = () => {
        infoEl.textContent = '⚠️ Ошибка WebSocket';
        infoEl.style.background = 'rgba(200, 100, 0, 0.75)';
    };
}

function sendCubePosition(cube) {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            type: 'cube_move',
            cube_id: cube.userData.id,
            position: {
                x: +cube.position.x.toFixed(3),
                y: +cube.position.y.toFixed(3),
                z: +cube.position.z.toFixed(3),
            },
        }));
    }
}

// ============ Отслеживание мыши для курсора ============
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();
const plane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);

window.addEventListener('mousemove', (event) => {
    mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
    mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

    raycaster.setFromCamera(mouse, camera);
    const intersection = new THREE.Vector3();
    raycaster.ray.intersectPlane(plane, intersection);

    if (intersection && ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            type: 'cursor_move',
            position: {
                x: +intersection.x.toFixed(3),
                y: +intersection.y.toFixed(3),
                z: +intersection.z.toFixed(3),
            },
        }));
    }
});

// ============ Запуск ============
connectWebSocket();

// ============ Анимация ============
function animate() {
    requestAnimationFrame(animate);
    orbitControls.update();
    renderer.render(scene, camera);
}
animate();

// ============ Ресайз ============
window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});