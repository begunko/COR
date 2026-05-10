// static/js/app/ToolHandler.js
import { Toolbar } from '../tools/toolbar.js';

export class ToolHandler {
    constructor(onCreateObject, onObjectCreated, onStatusChange) {
        this.onCreateObject = onCreateObject;
        this.onObjectCreated = onObjectCreated;
        this.onStatusChange = onStatusChange;
        this.toolbar = new Toolbar('#toolbar', (tool) => this._handleTool(tool));
    }

    load(worldId = null) {
        this.toolbar.loadTools(worldId);
    }

    _handleTool(tool) {
        this.onStatusChange(`🔧 Инструмент: ${tool.display_name}`, 'rgba(100, 50, 0, 0.85)');

        if (tool.tool_type === 'create_mesh') {
            const params = tool.default_params || {};
            const newObject = this.onCreateObject(params);
            if (this.onObjectCreated) {
                this.onObjectCreated(newObject, params);
            }
        }

        setTimeout(() => this.onStatusChange('🟢 Подключено', 'rgba(0, 150, 0, 0.75)'), 2000);
    }
}