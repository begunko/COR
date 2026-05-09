import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

export class SceneManager {
    constructor() {
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.orbitControls = null;
        this.clock = new THREE.Clock();
    }

    init() {
        // Сцена
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x1a1a2e);

        // Сетка
        const grid = new THREE.GridHelper(20, 20, 0x444466, 0x222244);
        this.scene.add(grid);

        // Камера
        this.camera = new THREE.PerspectiveCamera(
            60, window.innerWidth / window.innerHeight, 0.1, 1000
        );
        this.camera.position.set(5, 8, 10);
        this.camera.lookAt(0, 0, 0);

        // Рендерер
        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        document.body.appendChild(this.renderer.domElement);

        // OrbitControls
        this.orbitControls = new OrbitControls(this.camera, this.renderer.domElement);
        this.orbitControls.enableDamping = true;
        this.orbitControls.dampingFactor = 0.08;
        this.orbitControls.target.set(0, 0.5, 0);

        // Освещение
        this.setupLighting();

        // Пол
        this.setupFloor();

        // Ресайз
        window.addEventListener('resize', () => this.onResize());

        // Анимация
        this.animate();
    }

    setupLighting() {
        const ambient = new THREE.AmbientLight(0x404060, 2.5);
        this.scene.add(ambient);

        const dir = new THREE.DirectionalLight(0xffffff, 4);
        dir.position.set(5, 10, 5);
        dir.castShadow = true;
        dir.shadow.mapSize.width = 1024;
        dir.shadow.mapSize.height = 1024;
        dir.shadow.camera.near = 0.5;
        dir.shadow.camera.far = 50;
        this.scene.add(dir);
    }

    setupFloor() {
        const floor = new THREE.Mesh(
            new THREE.PlaneGeometry(20, 20),
            new THREE.ShadowMaterial({ opacity: 0.3 })
        );
        floor.rotation.x = -Math.PI / 2;
        floor.receiveShadow = true;
        this.scene.add(floor);
    }

    onResize() {
        this.camera.aspect = window.innerWidth / window.innerHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(window.innerWidth, window.innerHeight);
    }

    animate() {
        requestAnimationFrame(() => this.animate());
        this.orbitControls.update();
        this.renderer.render(this.scene, this.camera);
    }

    add(object) {
        this.scene.add(object);
    }

    remove(object) {
        this.scene.remove(object);
    }

    getDomElement() {
        return this.renderer.domElement;
    }
}