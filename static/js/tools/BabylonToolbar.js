// static/js/tools/BabylonToolbar.js
// ==============================================================================
// ТУЛБАР — инструменты из базы данных (иконки тоже из базы)
// ==============================================================================

import * as BABYLON from '../core/BabylonBridge.js';
import { Config } from '../core/Config.js';

export class BabylonToolbar {
    constructor(scene, sceneManager, callbacks = {}) {
        this.scene = scene;
        this.sm = sceneManager;
        this.callbacks = callbacks;
        this.gui = null;
    }

    async create() {
        this.gui = BABYLON.GUI.AdvancedDynamicTexture.CreateFullscreenUI('toolbar-ui');
        this._createGizmoPanel();
        await this._loadFromDatabase();
    }

    async _loadFromDatabase() {
        try {
            const response = await fetch(Config.toolbarUrl);
            const data = await response.json();
            const toolkits = data.toolkits || [];

            if (toolkits.length === 0) {
                console.warn('⚠️ База пуста. Создай инструменты через: python manage.py shell');
                return;
            }

            // Создаём панель для кнопок
            const panel = new BABYLON.GUI.StackPanel('tool-panel');
            panel.width = '56px';
            panel.horizontalAlignment = BABYLON.GUI.Control.HORIZONTAL_ALIGNMENT_LEFT;
            panel.verticalAlignment = BABYLON.GUI.Control.VERTICAL_ALIGNMENT_CENTER;
            panel.paddingLeft = '12px';
            panel.spacing = 8;
            this.gui.addControl(panel);

            // Для каждого набора — разделитель и кнопки
            toolkits.forEach((toolkit, kitIndex) => {
                // Разделитель между наборами (кроме первого)
                if (kitIndex > 0) {
                    const sep = new BABYLON.GUI.Rectangle(`sep-${kitIndex}`);
                    sep.height = '2px';
                    sep.width = '48px';
                    sep.background = 'rgba(255, 102, 0, 0.3)';
                    sep.cornerRadius = 2;
                    panel.addControl(sep);
                }

                // Кнопки инструментов
                (toolkit.tools || []).forEach(tool => {
                    const params = tool.default_params || {};
                    // Иконка из базы (toolkit.icon) или эмодзи по умолчанию
                    const icon = toolkit.icon || '📦';

                    const btn = this._createToolButton(
                        tool.name,
                        icon,
                        tool.display_name || tool.name,
                        () => {
                            if (this.callbacks.onToolSelected) {
                                this.callbacks.onToolSelected(tool);
                            }
                            if (this.callbacks.onStatusChange) {
                                this.callbacks.onStatusChange(`✅ ${tool.display_name || tool.name}`);
                                setTimeout(() => this.callbacks.onStatusChange('🟢 Подключено'), 2000);
                            }
                        }
                    );
                    panel.addControl(btn);
                });
            });

        } catch (err) {
            console.warn('⚠️ База недоступна:', err.message);
        }
    }

    _createGizmoPanel() {
        const panel = new BABYLON.GUI.StackPanel('gizmo-panel');
        panel.isVertical = false;
        panel.horizontalAlignment = BABYLON.GUI.Control.HORIZONTAL_ALIGNMENT_CENTER;
        panel.verticalAlignment = BABYLON.GUI.Control.VERTICAL_ALIGNMENT_BOTTOM;
        panel.paddingBottom = '20px';
        panel.height = '44px';
        panel.spacing = 8;
        this.gui.addControl(panel);

        // Перемещение / Вращение / Масштаб
        [
            { label: '↕', mode: 'translate' },
            { label: '↻', mode: 'rotate' },
            { label: '⤢', mode: 'scale' },
        ].forEach(({ label, mode }) => {
            const btn = this._createButton(
                `gizmo-${mode}`, label,
                () => {
                    this.sm.setGizmoMode(mode);
                    panel.children.forEach(c => c.background = 'rgba(30, 30, 60, 0.8)');
                    btn.background = 'rgba(255, 102, 0, 0.8)';
                },
                '40px', '40px', 'rgba(30, 30, 60, 0.8)', '#aaaaaa'
            );
            panel.addControl(btn);
        });

        // Удаление
        const delBtn = this._createButton(
            'delete-btn', '✕',
            () => { if (this.callbacks.onDelete) this.callbacks.onDelete(); },
            '40px', '40px', 'rgba(60, 20, 20, 0.6)', '#ff6666'
        );
        panel.addControl(delBtn);
    }

    _createToolButton(name, icon, hint, onClick) {
        return this._createButton(name, icon, onClick, '48px', '48px', 'rgba(30, 30, 60, 0.85)', '#ffffff', hint);
    }

    _createButton(name, text, onClick, w = '48px', h = '48px', bg = 'rgba(30, 30, 60, 0.85)', color = '#ffffff', hint = null) {
        const btn = BABYLON.GUI.Button.CreateSimpleButton(name, text);
        btn.width = w;
        btn.height = h;
        btn.color = color;
        btn.background = bg;
        btn.cornerRadius = 10;
        btn.thickness = 1;

        if (hint) {
            btn.onPointerEnterObservable.add(() => {
                btn.background = 'rgba(255, 102, 0, 0.7)';
                if (this.callbacks.onStatusChange) this.callbacks.onStatusChange(hint);
            });
            btn.onPointerOutObservable.add(() => {
                btn.background = bg;
                if (this.callbacks.onStatusChange) this.callbacks.onStatusChange('🟢 Подключено');
            });
        }

        btn.onPointerClickObservable.add(onClick);
        return btn;
    }
}