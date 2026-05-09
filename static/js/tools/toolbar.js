export class Toolbar {
    constructor(containerSelector, onToolSelected) {
        this.container = document.querySelector(containerSelector);
        this.onToolSelected = onToolSelected;
        this.activeTool = null;
        this.tools = [];
    }

    async loadTools(worldId = null) {
        try {
            const url = worldId
                ? `/api/v1/toolbar/world/${worldId}/`
                : '/api/v1/toolbar/';
            const response = await fetch(url);
            const data = await response.json();
            this.tools = data.tools || [];
        } catch (error) {
            console.error('Failed to load tools, using defaults:', error);
            this.tools = [
                { id: 'move', name: 'move', display_name: 'Перемещение', tool_type: 'transform', order: 0, icon_svg: '⬌' },
                { id: 'cube', name: 'cube', display_name: 'Куб', tool_type: 'create_mesh', order: 1, icon_svg: '◻' },
            ];
        }
        this.render();
    }

    render() {
        if (!this.container) return;
        this.container.innerHTML = '';

        this.tools.forEach(tool => {
            const button = document.createElement('div');
            button.className = 'toolbar-button';
            button.title = tool.display_name;
            button.dataset.toolId = tool.id;

            const iconSpan = document.createElement('span');
            iconSpan.className = 'toolbar-icon';

            if (tool.icon_svg && tool.icon_svg.trim().startsWith('<')) {
                iconSpan.innerHTML = tool.icon_svg;
            } else {
                iconSpan.textContent = tool.icon_svg || tool.display_name.charAt(0);
            }
            button.appendChild(iconSpan);

            const label = document.createElement('span');
            label.className = 'toolbar-label';
            label.textContent = tool.display_name;
            button.appendChild(label);

            button.addEventListener('click', () => {
                this.setActiveTool(tool, button);
            });

            this.container.appendChild(button);
        });
    }

    setActiveTool(tool, buttonElement) {
        const prev = this.container?.querySelector('.toolbar-button.active');
        if (prev) prev.classList.remove('active');
        if (buttonElement) buttonElement.classList.add('active');

        this.activeTool = tool;
        if (this.onToolSelected) this.onToolSelected(tool);
    }
}