// static/js/app/WorldView.js
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

        this.dragManager = new DragManager(this.sceneManager, (object) => {
            if (this.onObjectDragged) this.onObjectDragged(object);
        });
        this.dragManager.init();

        this.gizmo = new TransformGizmo(this.sceneManager);
        this.gizmo.init();
        this.gizmo.onObjectChanged = (object) => {
            if (this.onObjectDragged) this.onObjectDragged(object);
        };

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

            // Ищем среди ВСЕХ дочерних объектов draggable
            const allTargets = [];
            this.dragManager.draggableObjects.forEach(obj => {
                obj.traverse(child => {
                    if (child.isMesh) allTargets.push(child);
                });
            });

            const intersects = raycaster.intersectObjects(allTargets, false);

            if (intersects.length > 0) {
                // Поднимаемся до draggable родителя
                let obj = intersects[0].object;
                while (obj && !this.dragManager.draggableObjects.includes(obj)) {
                    obj = obj.parent;
                }
                if (obj) {
                    this.selectObject(obj);
                }
            } else {
                this.deselectAll();
            }
        });
    }

    selectObject(object) {
        if (this.selectedObject === object) return;
        this.deselectAll();
        this.selectedObject = object;
        this.dragManager.removeDraggable(object);
        this.gizmo.attach(object);
        this.showOutline(object);
        if (this.onObjectSelected) this.onObjectSelected(object);
    }

    deselectAll() {
        if (this.selectedObject) {
            this.hideOutline(this.selectedObject);
            this.dragManager.addDraggable(this.selectedObject);
            this.selectedObject = null;
        }
        this.gizmo.detach();
    }

    showOutline(object) {
        object.traverse(child => {
            if (child.material && child.material.emissive) {
                child.material.emissive.set(0x331100);
            }
        });
    }

    hideOutline(object) {
        object.traverse(child => {
            if (child.material && child.material.emissive) {
                child.material.emissive.set(0x000000);
            }
        });
    }

    setGizmoMode(mode) { this.gizmo.setMode(mode); return this.gizmo.mode; }

    createObject(params, position = null, objectId = null) {
        const obj = createMeshFromParams(params, position);
        if (objectId) obj.userData.id = objectId;
        this.sceneManager.add(obj);
        this.allObjects[obj.userData.id] = { mesh: obj, params: params };
        // Добавляем только родительский объект в drag
        this.dragManager.addDraggable(obj);
        setTimeout(() => this.selectObject(obj), 50);
        return obj;
    }

    updateOrCreateObject(objectId, params, position, rotation = null, scale = null) {
        const entry = this.allObjects[objectId];
        if (entry && entry.mesh) {
            entry.mesh.position.set(position.x, position.y, position.z);
            if (rotation) entry.mesh.rotation.set(rotation.x, rotation.y, rotation.z);
            if (scale) entry.mesh.scale.set(scale.x, scale.y, scale.z);
            if (params && Object.keys(params).length > 0) entry.params = params;
        } else {
            const createParams = params && Object.keys(params).length > 0 ? params : { geometry: 'BoxGeometry', color: '#ff6600' };
            const obj = createMeshFromParams(createParams, position);
            obj.userData.id = objectId;
            obj.userData.params = createParams;
            this.sceneManager.add(obj);
            this.allObjects[objectId] = { mesh: obj, params: createParams };
            this.dragManager.addDraggable(obj);
        }
    }

    loadFromServerData(cubesData) {
        for (const [objId, objData] of Object.entries(cubesData)) {
            const params = objData.params || {};
            const obj = createMeshFromParams(params, objData.position);
            obj.userData.id = objId;
            obj.userData.params = params;
            if (objData.rotation) obj.rotation.set(objData.rotation.x, objData.rotation.y, objData.rotation.z);
            if (objData.scale) obj.scale.set(objData.scale.x, objData.scale.y, objData.scale.z);
            this.sceneManager.add(obj);
            this.allObjects[objId] = { mesh: obj, params: params };
            this.dragManager.addDraggable(obj);
        }
    }

    getMesh(objectId) { return this.allObjects[objectId]?.mesh || null; }

    getAllObjectsData() {
        const data = {};
        for (const [id, entry] of Object.entries(this.allObjects)) {
            // Используем serverId как ключ для сохранения (если есть)
            const saveId = entry.mesh.userData.serverId || id;
            data[saveId] = {
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
                type: entry.params.geometry || 'BoxGeometry',
                params: entry.params,
            };
        }
        return data;
    }
}
