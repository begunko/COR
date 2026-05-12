// static/js/core/BabylonScene.js
// ==============================================================================
// СЦЕНА НА BABYLON.JS — тени, коллизии, сетка, гизмо
// ==============================================================================

import * as BABYLON from './BabylonBridge.js';

export class BabylonSceneManager {
    constructor() {
        this.engine = null;
        this.scene = null;
        this.camera = null;
        this.canvas = null;
        this.gizmoManager = null;
        this.shadowGenerator = null;
        this.sun = null;
    }

    init() {
        // 1. Canvas
        this.canvas = document.createElement('canvas');
        this.canvas.style.display = 'block';
        this.canvas.style.width = '100%';
        this.canvas.style.height = '100%';
        this.canvas.style.outline = 'none';
        document.body.appendChild(this.canvas);

        // 2. Engine
        this.engine = new BABYLON.Engine(this.canvas, true, {
            preserveDrawingBuffer: true,
            stencil: true,
            antialias: true,
        });

        // 3. Scene
        this.scene = new BABYLON.Scene(this.engine);
        this.scene.clearColor = new BABYLON.Color4(0.1, 0.1, 0.18, 1);

        // 4. Камера
        this.camera = new BABYLON.ArcRotateCamera(
            'camera',
            -Math.PI / 4,
            Math.PI / 3,
            15,
            new BABYLON.Vector3(0, 1, 0),
            this.scene
        );
        this.camera.lowerRadiusLimit = 2;
        this.camera.upperRadiusLimit = 50;
        this.camera.lowerBetaLimit = 0.1;
        this.camera.upperBetaLimit = Math.PI / 2 + 0.3;
        this.camera.inertia = 0.8;
        this.camera.panningInertia = 0.5;
        this.camera.attachControl(this.canvas, true);

        // 5. Освещение
        // Ambient
        const ambient = new BABYLON.HemisphericLight(
            'ambient',
            new BABYLON.Vector3(0, 1, 0),
            this.scene
        );
        ambient.intensity = 0.4;
        ambient.diffuse = new BABYLON.Color3(0.3, 0.3, 0.45);

        // Солнце (направленный свет)
        this.sun = new BABYLON.DirectionalLight(
            'sun',
            new BABYLON.Vector3(0.5, -1, 0.5),
            this.scene
        );
        this.sun.intensity = 1.2;
        this.sun.diffuse = new BABYLON.Color3(1, 0.95, 0.85);
        this.sun.specular = new BABYLON.Color3(1, 1, 1);

        // 6. ТЕНИ
        this.shadowGenerator = new BABYLON.ShadowGenerator(2048, this.sun);
        this.shadowGenerator.useBlurExponentialShadowMap = true;
        this.shadowGenerator.blurKernel = 32;
        this.shadowGenerator.darkness = 0.4;
        this.shadowGenerator.bias = 0.0001;
        this.shadowGenerator.useKernelBlur = true;
        this.shadowGenerator.blurScale = 4;

        // 7. Сетка (Ground)
        const gridMat = new BABYLON.GridMaterial('grid', this.scene);
        gridMat.majorUnitFrequency = 1;
        gridMat.minorUnitVisibility = 0.3;
        gridMat.gridRatio = 1;
        gridMat.mainColor = new BABYLON.Color3(0.8, 0.8, 0.9);
        gridMat.lineColor = new BABYLON.Color3(0.25, 0.25, 0.4);
        gridMat.backFaceCulling = false;

        const ground = BABYLON.MeshBuilder.CreateGround('ground', {
            width: 30,
            height: 30,
        }, this.scene);
        ground.material = gridMat;
        ground.position.y = -0.01;
        ground.isPickable = false;
        ground.receiveShadows = true;

        // 8. Коллизии
        this.scene.collisionsEnabled = true;
        this.scene.gravity = new BABYLON.Vector3(0, -9.81, 0);

        // Коллизия для камеры
        this.camera.checkCollisions = true;
        this.camera.collisionRadius = new BABYLON.Vector3(0.5, 0.5, 0.5);

        // Коллизия для пола
        ground.checkCollisions = true;

        // 9. Фоновая подсветка (Environment)
        this.scene.environmentIntensity = 0.3;

        // 10. GizmoManager
        this.gizmoManager = new BABYLON.GizmoManager(this.scene);
        this.gizmoManager.positionGizmoEnabled = true;
        this.gizmoManager.rotationGizmoEnabled = false;
        this.gizmoManager.scaleGizmoEnabled = false;

        if (this.gizmoManager.gizmos?.positionGizmo) {
            this.gizmoManager.gizmos.positionGizmo.scaleRatio = 1.5;
        }
        if (this.gizmoManager.gizmos?.rotationGizmo) {
            this.gizmoManager.gizmos.rotationGizmo.scaleRatio = 1.5;
        }
        if (this.gizmoManager.gizmos?.scaleGizmo) {
            this.gizmoManager.gizmos.scaleGizmo.scaleRatio = 1.5;
        }

        // 11. Автоматическое добавление теней для новых мешей
        const self = this;
        this.scene.onNewMeshAddedObservable.add((mesh) => {
            if (mesh && mesh.name !== 'ground') {
                self.shadowGenerator.addShadowCaster(mesh, true);
                mesh.receiveShadows = true;
            }
        });

        // 12. Render loop
        this.engine.runRenderLoop(() => {
            this.scene.render();
        });

        // 13. Resize
        window.addEventListener('resize', () => this.engine.resize());

        console.log('🎮 Babylon.js сцена инициализирована');
        console.log('   ✅ Тени (Shadow Map 1024)');
        console.log('   ✅ Коллизии (gravity: 9.81)');
        console.log('   ✅ Гизмо (translate/rotate/scale)');
        console.log('   ✅ Grid Material');
    }

    setGizmoMode(mode) {
        const map = {
            'translate': 'position',
            'rotate': 'rotation',
            'scale': 'scale',
        };
        const gizmoType = map[mode] || 'position';

        this.gizmoManager.positionGizmoEnabled = (gizmoType === 'position');
        this.gizmoManager.rotationGizmoEnabled = (gizmoType === 'rotation');
        this.gizmoManager.scaleGizmoEnabled = (gizmoType === 'scale');
    }

    add(object) {
        if (object && object.parent !== this.scene) {
            object.setParent(null);
        }
    }

    remove(object) {
        if (object) {
            object.dispose();
        }
    }

    getDomElement() {
        return this.canvas;
    }

    showInspector() {
        if (this.scene?.debugLayer) {
            this.scene.debugLayer.show({ embedMode: true });
        }
    }

    /** Включает/выключает физику для объекта */
    enablePhysics(mesh, enable = true) {
        if (mesh) {
            mesh.checkCollisions = enable;
        }
    }

    /** Создаёт точку на полу под указателем */
    getGroundPosition() {
        const pickInfo = this.scene.pick(
            this.scene.pointerX,
            this.scene.pointerY,
            (mesh) => mesh.name === 'ground'
        );
        if (pickInfo.hit) {
            return pickInfo.pickedPoint;
        }
        return new BABYLON.Vector3(0, 0, 0);
    }
}