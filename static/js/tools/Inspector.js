// static/js/tools/Inspector.js
// ==============================================================================
// ИНСПЕКТОР — показывает свойства выделенного объекта
// ==============================================================================

import * as BABYLON from '../core/BabylonBridge.js';

export class Inspector {
    constructor(scene) {
        this.scene = scene;
        this.selectedMesh = null;
        this.gui = null;
        this.panel = null;
        this._labels = {};
    }

    create() {
        this.gui = BABYLON.GUI.AdvancedDynamicTexture.CreateFullscreenUI('inspector-ui');

        // Панель справа
        this.panel = new BABYLON.GUI.StackPanel('inspector-panel');
        this.panel.width = '260px';
        this.panel.horizontalAlignment = BABYLON.GUI.Control.HORIZONTAL_ALIGNMENT_RIGHT;
        this.panel.verticalAlignment = BABYLON.GUI.Control.VERTICAL_ALIGNMENT_TOP;
        this.panel.paddingTop = '10px';
        this.panel.paddingRight = '10px';
        this.panel.spacing = 4;
        this.panel.background = 'rgba(20, 20, 40, 0.9)';
        this.panel.cornerRadius = 12;
        this.panel.paddingLeft = '10px';
        this.panel.paddingBottom = '10px';
        this.panel.isVisible = false;
        this.gui.addControl(this.panel);

        // Заголовок
        this._addLabel('title', 'Инспектор', '16px', '#ff6600');
        this._addSeparator();
        this._addLabel('name', '', '14px', '#ffffff');
        this._addSeparator();
        this._addLabel('position', '', '12px', '#aaaaaa');
        this._addLabel('rotation', '', '12px', '#aaaaaa');
        this._addLabel('scale', '', '12px', '#aaaaaa');
        this._addSeparator();
        this._addLabel('color', '', '12px', '#aaaaaa');
    }

    attach(mesh) {
        this.selectedMesh = mesh;
        this._update();
        this.panel.isVisible = true;
    }

    detach() {
        this.selectedMesh = null;
        this.panel.isVisible = false;
    }

    _update() {
        if (!this.selectedMesh) return;

        const m = this.selectedMesh;
        const meta = m.metadata || {};

        this._labels['name'].text = `📦 ${meta.geometry || meta.type || 'Объект'}`;
        this._labels['position'].text = `📍 Позиция: ${m.position.x.toFixed(2)}, ${m.position.y.toFixed(2)}, ${m.position.z.toFixed(2)}`;
        this._labels['rotation'].text = `🔄 Поворот: ${(m.rotation.x * 180 / Math.PI).toFixed(1)}°, ${(m.rotation.y * 180 / Math.PI).toFixed(1)}°, ${(m.rotation.z * 180 / Math.PI).toFixed(1)}°`;
        this._labels['scale'].text = `📏 Масштаб: ${m.scaling.x.toFixed(2)} × ${m.scaling.y.toFixed(2)} × ${m.scaling.z.toFixed(2)}`;
        this._labels['color'].text = `🎨 Цвет: ${meta.color || '#ffffff'}`;
    }

    _addLabel(key, text, fontSize = '12px', color = '#ffffff') {
        const label = new BABYLON.GUI.TextBlock(key, text);
        label.fontSize = fontSize;
        label.color = color;
        label.textHorizontalAlignment = BABYLON.GUI.Control.HORIZONTAL_ALIGNMENT_LEFT;
        label.height = fontSize === '16px' ? '24px' : '20px';
        this.panel.addControl(label);
        this._labels[key] = label;
    }

    _addSeparator() {
        const sep = new BABYLON.GUI.Rectangle('sep');
        sep.height = '1px';
        sep.background = 'rgba(255, 102, 0, 0.2)';
        sep.cornerRadius = 1;
        sep.paddingTop = '4px';
        sep.paddingBottom = '4px';
        this.panel.addControl(sep);
    }
}