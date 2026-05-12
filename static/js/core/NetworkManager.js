// static/js/core/NetworkManager.js
// ==============================================================================
// СЕТЕВОЙ МЕНЕДЖЕР — HTTP API для сохранения и загрузки
// ==============================================================================

import { Config } from './Config.js';

export class NetworkManager {
    /**
     * Загрузить объекты чанка с сервера
     */
    static async loadChunk() {
        try {
            const response = await fetch(Config.chunkLoadUrl);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (err) {
            console.error('❌ Ошибка загрузки чанка:', err);
            return { objects: {}, chunk_type: 'void' };
        }
    }

    /**
     * Сохранить объекты чанка на сервер
     */
    static async saveChunk(objectsData) {
        try {
            const body = {
                objects: objectsData,
                chunk_type: 'full',
            };
            if (Config.worldId) body.world_id = Config.worldId;

            const response = await fetch(Config.chunkSaveUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body),
            });
            return await response.json();
        } catch (err) {
            console.error('❌ Ошибка сохранения чанка:', err);
            return null;
        }
    }

    /**
     * Загрузить список инструментов из базы
     */
    static async loadToolbar() {
        try {
            const response = await fetch(Config.toolbarUrl);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (err) {
            console.warn('⚠️ Тулбар из базы не загружен:', err.message);
            return { toolkits: [] };
        }
    }

    /**
     * Загрузить список ассетов из базы
     */
    static async loadAssets() {
        try {
            const response = await fetch(Config.assetsUrl);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (err) {
            console.warn('⚠️ Ассеты не загружены:', err.message);
            return { assets: [] };
        }
    }
}