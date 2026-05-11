// static/js/controls/DragManager.js
import * as THREE from 'three';

export class DragManager {
    constructor(sceneManager, onDragCallback) {
        this.sceneManager = sceneManager;
        this.onDragCallback = onDragCallback;
        this.draggableObjects = [];
        this.isDragging = false;
        this.selectedObject = null;

        this.raycaster = new THREE.Raycaster();
        this.mouse = new THREE.Vector2();
        this.plane = new THREE.Plane();
        this.offset = new THREE.Vector3();
        this.intersection = new THREE.Vector3();

        this._onPointerDown = this._onPointerDown.bind(this);
        this._onPointerMove = this._onPointerMove.bind(this);
        this._onPointerUp = this._onPointerUp.bind(this);
    }

    init() {
        const domElement = this.sceneManager.getDomElement();

        // Удаляем старые слушатели если есть
        domElement.removeEventListener('pointerdown', this._onPointerDown);
        domElement.removeEventListener('pointermove', this._onPointerMove);
        domElement.removeEventListener('pointerup', this._onPointerUp);

        if (this.draggableObjects.length === 0) return;

        domElement.addEventListener('pointerdown', this._onPointerDown);
        domElement.addEventListener('pointermove', this._onPointerMove);
        domElement.addEventListener('pointerup', this._onPointerUp);
    }

    _findDraggableParent(object) {
        // Поднимаемся по иерархии пока не найдём draggable объект
        let current = object;
        while (current) {
            if (this.draggableObjects.includes(current)) {
                return current;
            }
            current = current.parent;
        }
        return null;
    }

    _onPointerDown(event) {
        if (event.button !== 0) return; // только левая кнопка

        const domElement = this.sceneManager.getDomElement();
        const rect = domElement.getBoundingClientRect();

        this.mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        this.mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

        this.raycaster.setFromCamera(this.mouse, this.sceneManager.camera);

        // Рекурсивно ищем пересечения со всеми draggable и их дочерними
        const allTargets = [];
        this.draggableObjects.forEach(obj => {
            obj.traverse(child => {
                if (child.isMesh) allTargets.push(child);
            });
        });

        const intersects = this.raycaster.intersectObjects(allTargets, false);

        if (intersects.length > 0) {
            // Нашли дочерний объект — поднимаемся до draggable родителя
            const childObject = intersects[0].object;
            const draggableParent = this._findDraggableParent(childObject);

            if (draggableParent) {
                this.selectedObject = draggableParent;
                this.isDragging = true;
                this.sceneManager.orbitControls.enabled = false;

                // Плоскость для перемещения
                this.plane.setFromNormalAndCoplanarPoint(
                    this.sceneManager.camera.getWorldDirection(new THREE.Vector3()),
                    draggableParent.position
                );

                // Сохраняем смещение
                if (this.raycaster.ray.intersectPlane(this.plane, this.intersection)) {
                    this.offset.copy(this.intersection).sub(draggableParent.position);
                }

                // Подсветка
                draggableParent.traverse(child => {
                    if (child.material && child.material.emissive) {
                        child.material.emissive.set(0x331100);
                    }
                });

                domElement.style.cursor = 'move';
            }
        }
    }

    _onPointerMove(event) {
        if (!this.isDragging || !this.selectedObject) return;

        const domElement = this.sceneManager.getDomElement();
        const rect = domElement.getBoundingClientRect();

        this.mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        this.mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

        this.raycaster.setFromCamera(this.mouse, this.sceneManager.camera);

        if (this.raycaster.ray.intersectPlane(this.plane, this.intersection)) {
            this.selectedObject.position.copy(this.intersection.sub(this.offset));

            if (this.onDragCallback) {
                this.onDragCallback(this.selectedObject);
            }
        }
    }

    _onPointerUp() {
        if (this.selectedObject) {
            // Убираем подсветку
            this.selectedObject.traverse(child => {
                if (child.material && child.material.emissive) {
                    child.material.emissive.set(0x000000);
                }
            });
        }

        this.isDragging = false;
        this.selectedObject = null;
        this.sceneManager.orbitControls.enabled = true;
        this.sceneManager.getDomElement().style.cursor = '';
    }

    addDraggable(object) {
        if (!this.draggableObjects.includes(object)) {
            this.draggableObjects.push(object);
            this.init();
        }
    }

    removeDraggable(object) {
        const index = this.draggableObjects.indexOf(object);
        if (index > -1) {
            this.draggableObjects.splice(index, 1);
            this.init();
        }
    }
}