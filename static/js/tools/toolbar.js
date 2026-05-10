// static/js/tools/toolbar.js
// ==============================================================================
// ТУЛБАР — панель инструментов редактора
//
// Новая структура: наборы (Toolkit) → инструменты (Tool)
// На панели — иконки наборов, при клике раскрывается список инструментов.
// ==============================================================================

export class Toolbar {
    constructor(containerSelector, onToolSelected) {
        this.container = document.querySelector(containerSelector);
        this.onToolSelected = onToolSelected;
        this.activeTool = null;
        this.toolkits = [];  // теперь наборы, не инструменты
        this.expandedToolkit = null;  // какой набор раскрыт
    }

    async loadTools(worldId = null) {
        try {
            const url = worldId
                ? `/api/v1/toolbar/world/${worldId}/`
                : '/api/v1/toolbar/';
            const response = await fetch(url);
            const data = await response.json();
            this.toolkits = data.toolkits || [];
        } catch (error) {
            console.error('Failed to load tools, using defaults:', error);
            this.toolkits = [];
        }
        this.render();
    }

    render() {
        if (!this.container) return;
        this.container.innerHTML = '';

        this.toolkits.forEach(toolkit => {
            // Кнопка набора
            const button = document.createElement('div');
            button.className = 'toolbar-button';
            button.title = toolkit.name;
            button.dataset.toolkitId = toolkit.id;

            // Иконка набора (эмодзи)
            const iconSpan = document.createElement('span');
            iconSpan.className = 'toolbar-icon';
            iconSpan.textContent = toolkit.icon || '📦';
            button.appendChild(iconSpan);

            // Подсказка
            const label = document.createElement('span');
            label.className = 'toolbar-label';
            label.textContent = toolkit.name;
            button.appendChild(label);

            // При клике — раскрываем/скрываем набор
            button.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleToolkit(toolkit, button);
            });

            this.container.appendChild(button);

            // Выпадающий список инструментов (скрыт по умолчанию)
            const dropdown = document.createElement('div');
            dropdown.className = 'toolkit-dropdown';
            dropdown.style.display = 'none';
            dropdown.dataset.toolkitId = toolkit.id;

            toolkit.tools.forEach(tool => {
                const toolItem = document.createElement('div');
                toolItem.className = 'toolkit-tool-item';
                toolItem.textContent = tool.display_name;
                toolItem.title = tool.name;

                toolItem.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.selectTool(tool, toolItem);
                    // Скрываем выпадашку после выбора
                    dropdown.style.display = 'none';
                });

                dropdown.appendChild(toolItem);
            });

            this.container.appendChild(dropdown);
        });

        // Клик вне тулбара — закрыть все выпадашки
        document.addEventListener('click', () => {
            this.closeAllDropdowns();
        });
    }

    toggleToolkit(toolkit, buttonElement) {
        const dropdown = this.container.querySelector(
            `.toolkit-dropdown[data-toolkit-id="${toolkit.id}"]`
        );
        if (!dropdown) return;

        // Закрываем все остальные
        this.closeAllDropdowns();

        // Переключаем текущий
        if (dropdown.style.display === 'none') {
            dropdown.style.display = 'block';
            // Позиционируем выпадашку справа от кнопки
            const btnRect = buttonElement.getBoundingClientRect();
            dropdown.style.position = 'fixed';
            dropdown.style.left = (btnRect.right + 8) + 'px';
            dropdown.style.top = btnRect.top + 'px';
        }
    }

    closeAllDropdowns() {
        const dropdowns = this.container.querySelectorAll('.toolkit-dropdown');
        dropdowns.forEach(d => d.style.display = 'none');
    }

    selectTool(tool, toolElement) {
        // Подсветка активного инструмента
        const prev = this.container.querySelector('.toolkit-tool-item.active');
        if (prev) prev.classList.remove('active');
        if (toolElement) toolElement.classList.add('active');

        this.activeTool = tool;
        if (this.onToolSelected) this.onToolSelected(tool);
    }
}