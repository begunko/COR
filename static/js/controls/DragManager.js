import { DragControls } from 'three/addons/controls/DragControls.js';

export class DragManager {
    constructor(sceneManager, onDragCallback) {
        this.sceneManager = sceneManager;
        this.onDragCallback = onDragCallback;
        this.dragControls = null;
        this.draggableObjects = [];
    }

    init() {
        if (this.dragControls) {
            this.dragControls.dispose();
        }

        this.dragControls = new DragControls(
            this.draggableObjects,
            this.sceneManager.camera,
            this.sceneManager.getDomElement()
        );

        this.dragControls.addEventListener('dragstart', (event) => {
            this.sceneManager.orbitControls.enabled = false;
            if (event.object.material.emissive) {
                event.object.material.emissive.set(0x331100);
            }
        });

        this.dragControls.addEventListener('drag', (event) => {
            if (this.onDragCallback) {
                this.onDragCallback(event.object);
            }
        });

        this.dragControls.addEventListener('dragend', (event) => {
            this.sceneManager.orbitControls.enabled = true;
            if (event.object.material.emissive) {
                event.object.material.emissive.set(0x000000);
            }
            // Сбрасываем захват
            this.sceneManager.orbitControls.target.copy(event.object.position);
        });

        // Отпускаем объект при клике правой кнопкой
        this.sceneManager.getDomElement().addEventListener('contextmenu', (e) => {
            e.preventDefault();
            this.releaseAll();
        });
    }

    releaseAll() {
        if (this.dragControls) {
            this.dragControls.deactivate();
            this.sceneManager.orbitControls.enabled = true;
        }
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