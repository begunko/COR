import { SceneManager } from '../core/Scene.js';
import { DragManager } from '../controls/DragManager.js';
import { TransformGizmo } from '../controls/TransformGizmo.js';
import { createMeshFromParams } from '../objects/MeshFactory.js';
import * as THREE from 'three';

export class WorldView {
    constructor() {
        this.sceneManager = new SceneManager();
        this.sceneManager.init();

        this.allObjects = {};
        this.onObjectDragged = null;
        this.onObjectSelected = null;
        this.selectedObject = null;

        // Drag (перетаскивание)
        this.dragManager = new DragManager(this.sceneManager, (object) => {
            if (this.onObjectDragged) {
                this.onObjectDragged(object);
            }
        });
        this.dragManager.init();

        // TransformGizmo
        this.gizmo = new TransformGizmo(this.sceneManager);
        this.gizmo.init();
        this.gizmo.onObjectChanged = (object) => {
            if (this.onObjectDragged) {
                this.onObjectDragged(object);
            }
        };

        // Клик для выбора объекта
        this.setupSelection();
    }

    setupSelection() {
        const raycaster = new THREE.Raycaster();
        const mouse = new THREE.Vector2();
        const domElement = this.sceneManager.getDomElement();

        domElement.addEventListener('click', (event) => {
            if (this.dragManager.isDragging) return;

            mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
            mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

            raycaster.setFromCamera(mouse, this.sceneManager.camera);

            // Ищем среди draggable объектов
            const intersects = raycaster.intersectObjects(this.dragManager.draggableObjects);

            if (intersects.length > 0) {
                this.selectObject(intersects[0].object);
            } else {
                this.deselectAll();
            }
        });
    }

    selectObject(object) {
        if (this.selectedObject === object) return;
        this.deselectAll();

        this.selectedObject = object;
        // Убираем из DragControls чтобы не конфликтовал с гизмо
        this.dragManager.removeDraggable(object);
        this.gizmo.attach(object);
        this.showOutline(object);

        if (this.onObjectSelected) {
            this.onObjectSelected(object);
        }
    }

    deselectAll() {
        if (this.selectedObject) {
            this.hideOutline(this.selectedObject);
            // Возвращаем в DragControls
            this.dragManager.addDraggable(this.selectedObject);
            this.selectedObject = null;
        }
        this.gizmo.detach();
    }

    showOutline(object) {
        if (object.material && object.material.emissive) {
            object.material.emissive.set(0x331100);
        }
    }

    hideOutline(object) {
        if (object.material && object.material.emissive) {
            object.material.emissive.set(0x000000);
        }
    }

    setGizmoMode(mode) {
        this.gizmo.setMode(mode);
        return this.gizmo.mode;
    }

    createObject(params, position = null, objectId = null) {
        const obj = createMeshFromParams(params, position);
        if (objectId) {
            obj.userData.id = objectId;
        }

        this.sceneManager.add(obj);
        this.allObjects[obj.userData.id] = { mesh: obj, params: params };
        this.dragManager.addDraggable(obj);

        // Автовыделение нового объекта
        setTimeout(() => this.selectObject(obj), 50);

        return obj;
    }

    updateOrCreateObject(objectId, params, position, rotation = null, scale = null) {
        const entry = this.allObjects[objectId];

        if (entry && entry.mesh) {
            entry.mesh.position.set(position.x, position.y, position.z);
            if (rotation) {
                entry.mesh.rotation.set(rotation.x, rotation.y, rotation.z);
            }
            if (scale) {
                entry.mesh.scale.set(scale.x, scale.y, scale.z);
            }
            if (params && Object.keys(params).length > 0) {
                entry.params = params;
            }
        } else {
            const createParams = params && Object.keys(params).length > 0
                ? params
                : { mesh_type: 'cube', color: '#ff6600' };

            const color = createParams.color || '#ff6600';
            const obj = createMeshFromParams({ ...createParams, color }, position);
            obj.userData.id = objectId;
            obj.userData.type = createParams.mesh_type || 'cube';
            obj.userData.params = createParams;

            this.sceneManager.add(obj);
            this.allObjects[objectId] = { mesh: obj, params: createParams };
            this.dragManager.addDraggable(obj);
        }
    }

    loadFromServerData(cubesData) {
        for (const [objId, objData] of Object.entries(cubesData)) {
            const params = objData.params || {};
            const color = objData.color || '#ff6600';
            const obj = createMeshFromParams({ ...params, color }, objData.position);
            obj.userData.id = objId;
            obj.userData.type = objData.type || 'cube';
            obj.userData.params = params;

            this.sceneManager.add(obj);
            this.allObjects[objId] = { mesh: obj, params: params };
            this.dragManager.addDraggable(obj);
        }
    }

    getMesh(objectId) {
        return this.allObjects[objectId]?.mesh || null;
    }

    getAllObjectsData() {
        const data = {};
        for (const [id, entry] of Object.entries(this.allObjects)) {
            data[id] = {
                color: entry.params.color || '#ff6600',
                position: {
                    x: +entry.mesh.position.x.toFixed(3),
                    y: +entry.mesh.position.y.toFixed(3),
                    z: +entry.mesh.position.z.toFixed(3),
                },
                rotation: {
                    x: +entry.mesh.rotation.x.toFixed(3),
                    y: +entry.mesh.rotation.y.toFixed(3),
                    z: +entry.mesh.rotation.z.toFixed(3),
                },
                scale: {
                    x: +entry.mesh.scale.x.toFixed(3),
                    y: +entry.mesh.scale.y.toFixed(3),
                    z: +entry.mesh.scale.z.toFixed(3),
                },
                type: entry.params.mesh_type || 'cube',
                params: entry.params,
            };
        }
        return data;
    }
}