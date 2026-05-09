import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { DragControls } from 'three/addons/controls/DragControls.js';

// ============ DOM-элементы ============
const infoEl = document.getElementById('info');

// ============ Сцена ============
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x1a1a2e);

// Сетка
const grid = new THREE.GridHelper(20, 20, 0x444466, 0x222244);
scene.add(grid);

// ============ Камера ============
const camera = new THREE.PerspectiveCamera(
    60, window.innerWidth / window.innerHeight, 0.1, 1000
);
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

// Пол для теней
const floor = new THREE.Mesh(
    new THREE.PlaneGeometry(20, 20),
    new THREE.ShadowMaterial({ opacity: 0.3 })
);
floor.rotation.x = -Math.PI / 2;
floor.receiveShadow = true;
scene.add(floor);

// ============ Куб ============
const cubeGeometry = new THREE.BoxGeometry(1, 1, 1);
const cubeMaterial = new THREE.MeshStandardMaterial({
    color: 0xff6600,
    roughness: 0.3,
    metalness: 0.1,
});
const cube = new THREE.Mesh(cubeGeometry, cubeMaterial);
cube.castShadow = true;
cube.receiveShadow = true;
cube.position.set(0, 0.5, 0);
scene.add(cube);

// ============ DragControls ============
const dragControls = new DragControls([cube], camera, renderer.domElement);

dragControls.addEventListener('dragstart', () => {
    orbitControls.enabled = false;
    cubeMaterial.emissive = new THREE.Color(0x331100);
});

dragControls.addEventListener('drag', () => {
    // Отправляем позицию через WebSocket
    sendPosition();
});

dragControls.addEventListener('dragend', () => {
    orbitControls.enabled = true;
    cubeMaterial.emissive = new THREE.Color(0x000000);
});

// ============ WebSocket ============
const CHUNK_ID = 'test-chunk-001';
let ws = null;

function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `ws://127.0.0.1:8000/ws/chunk/${CHUNK_ID}/`;

    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        infoEl.textContent = `🟢 Подключено к чанку: ${CHUNK_ID}`;
        infoEl.style.background = 'rgba(0, 150, 0, 0.75)';
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.type === 'init') {
            // Сервер прислал текущую позицию куба
            cube.position.set(
                data.position.x,
                data.position.y,
                data.position.z
            );
        }

        if (data.type === 'cube_moved') {
            // Другой пользователь передвинул куб
            cube.position.set(
                data.position.x,
                data.position.y,
                data.position.z
            );
            infoEl.textContent = `🔄 Куб передвинут: ${data.user}`;
            infoEl.style.background = 'rgba(0, 100, 200, 0.75)';

            // Через 2 секунды возвращаем обычный статус
            setTimeout(() => {
                if (ws && ws.readyState === WebSocket.OPEN) {
                    infoEl.textContent = `🟢 Подключено к чанку: ${CHUNK_ID}`;
                    infoEl.style.background = 'rgba(0, 150, 0, 0.75)';
                }
            }, 2000);
        }
    };

    ws.onclose = () => {
        infoEl.textContent = '🔴 Соединение потеряно. Переподключение...';
        infoEl.style.background = 'rgba(200, 0, 0, 0.75)';
        // Автопереподключение через 2 секунды
        setTimeout(connectWebSocket, 2000);
    };

    ws.onerror = () => {
        infoEl.textContent = '⚠️ Ошибка WebSocket';
        infoEl.style.background = 'rgba(200, 100, 0, 0.75)';
    };
}

function sendPosition() {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            position: {
                x: +cube.position.x.toFixed(3),
                y: +cube.position.y.toFixed(3),
                z: +cube.position.z.toFixed(3),
            },
            user: 'Я'
        }));
    }
}

// Запускаем подключение
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