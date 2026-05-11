// static/js/controls/DragManager.js
import { DragControls } from 'three/addons/controls/DragControls.js';

export class DragManager {
    constructor(sceneManager, onDragCallback) {
        this.sceneManager = sceneManager;
        this.onDragCallback = onDragCallback;
        this.dragControls = null;
        this.draggableObjects = [];
        this.isDragging = false;
    }

    init() {
        if (this.dragControls) {
            this.dragControls.dispose();
        }
        if (this.draggableObjects.length === 0) return;

        this.dragControls = new DragControls(
            this.draggableObjects,
            this.sceneManager.camera,
            this.sceneManager.getDomElement()
        );

        // Настройка: рекурсивно ищем объекты внутри групп
        this.dragControls.recursive = true;

        this.dragControls.addEventListener('dragstart', (event) => {
            this.isDragging = true;
            this.sceneManager.orbitControls.enabled = false;
            // Ищем родительский draggable объект
            let obj = event.object;
            while (obj && !this.draggableObjects.includes(obj)) {
                obj = obj.parent;
            }
            if (obj && obj !== event.object) {
                // Перемещаем родителя вместо дочернего
                event.object = obj;
            }
            if (event.object.material && event.object.material.emissive) {
                event.object.material.emissive.set(0x331100);
            } else if (event.object.traverse) {
                event.object.traverse(child => {
                    if (child.material && child.material.emissive) {
                        child.material.emissive.set(0x331100);
                    }
                });
            }
        });

        this.dragControls.addEventListener('drag', (event) => {
            if (this.onDragCallback) {
                let obj = event.object;
                while (obj && !this.draggableObjects.includes(obj)) {
                    obj = obj.parent;
                }
                this.onDragCallback(obj || event.object);
            }
        });

        this.dragControls.addEventListener('dragend', (event) => {
            this.isDragging = false;
            this.sceneManager.orbitControls.enabled = true;
            if (event.object.material && event.object.material.emissive) {
                event.object.material.emissive.set(0x000000);
            } else if (event.object.traverse) {
                event.object.traverse(child => {
                    if (child.material && child.material.emissive) {
                        child.material.emissive.set(0x000000);
                    }
                });
            }
        });
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