// static/js/core/Config.js
// ==============================================================================
// КОНФИГУРАЦИЯ — рабочая схема с двумя портами
// ==============================================================================

const urlParams = new URLSearchParams(window.location.search);

const HTTP_PORT = '8001';  // Django runserver (статика + API)
const WS_PORT = '8000';    // Daphne (WebSocket)

export const Config = {
    // Чанк и мир из URL
    chunkId: urlParams.get('chunk_id') || 'demo-chunk',
    worldId: urlParams.get('world_id') || null,

    // Порты (те самые, которые работают!)
    httpPort: HTTP_PORT,
    wsPort: WS_PORT,

    // Хост (без порта)
    hostname: window.location.hostname,

    // Полные URL
    get apiBase() { return `http://${this.hostname}:${this.httpPort}`; },
    get wsBase() { return `ws://${this.hostname}:${this.wsPort}`; },

    // API endpoints
    get chunkLoadUrl() { return `${this.apiBase}/api/chunk/${this.chunkId}/load/`; },
    get chunkSaveUrl() { return `${this.apiBase}/api/chunk/${this.chunkId}/save/`; },
    get toolbarUrl() { return `${this.apiBase}/api/v1/toolbar/${this.worldId ? `world/${this.worldId}/` : ''}`; },
    get assetsUrl() { return `${this.apiBase}/api/v1/assets/`; },
};

// Для отладки
console.log(`🌍 Мир: ${Config.worldId} | 📦 Чанк: ${Config.chunkId}`);
console.log(`🔗 HTTP: ${Config.apiBase} | WS: ${Config.wsBase}`);
