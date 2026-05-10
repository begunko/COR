import { TransformControls } from 'three/addons/controls/TransformControls.js';

export class TransformGizmo {
    constructor(sceneManager) {
        this.sceneManager = sceneManager;
        this.gizmo = null;
        this.attachedObject = null;
        this.isActive = false;
        this.mode = 'translate';
        this.onObjectChanged = null;
    }

    init() {
        this.gizmo = new TransformControls(
            this.sceneManager.camera,
            this.sceneManager.getDomElement()
        );

        this.gizmo.setMode(this.mode);
        this.gizmo.setSize(0.8);

        // Отключаем OrbitControls во время работы с гизмо
        this.gizmo.addEventListener('dragging-changed', (event) => {
            this.sceneManager.orbitControls.enabled = !event.value;
        });

        // При КАЖДОМ изменении объекта (позиция, поворот, масштаб)
        this.gizmo.addEventListener('objectChange', () => {
            if (this.attachedObject && this.onObjectChanged) {
                this.onObjectChanged(this.attachedObject);
            }
        });

        // Дополнительно: отслеживаем mouseUp для гарантированного сохранения
        this.gizmo.addEventListener('mouseUp', () => {
            if (this.attachedObject && this.onObjectChanged) {
                this.onObjectChanged(this.attachedObject);
            }
        });

        this.sceneManager.add(this.gizmo);
    }

    attach(object) {
        if (this.gizmo) {
            this.gizmo.attach(object);
            this.attachedObject = object;
            this.isActive = true;
        }
    }

    detach() {
        if (this.gizmo) {
            this.gizmo.detach();
            this.attachedObject = null;
            this.isActive = false;
        }
    }

    setMode(mode) {
        this.mode = mode;
        if (this.gizmo) {
            this.gizmo.setMode(mode);
        }
    }

    toggleMode() {
        const modes = ['translate', 'rotate', 'scale'];
        const currentIndex = modes.indexOf(this.mode);
        const nextIndex = (currentIndex + 1) % modes.length;
        this.setMode(modes[nextIndex]);
        return this.mode;
    }

    setEnabled(enabled) {
        if (this.gizmo) {
            this.gizmo.visible = enabled;
            if (!enabled) {
                this.detach();
            }
        }
    }
}