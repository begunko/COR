// static/js/core/RealtimeSync.js
// ==============================================================================
// СИНХРОНИЗАЦИЯ В РЕАЛЬНОМ ВРЕМЕНИ
// ==============================================================================

import { Config } from './Config.js';
import { SyncManager } from './SyncManager.js';
import { NetworkManager } from './NetworkManager.js';

export class RealtimeSync {
    /**
     * @param {Object} objectManager — экземпляр ObjectManager
     * @param {Function} onStatusChange — callback для статус-бара
     * @param {Function} getSelected — функция, возвращающая выделенный объект
     * @param {Function} deselectAll — функция снятия выделения
     */
    constructor(objectManager, onStatusChange, getSelected, deselectAll) {
        this.om = objectManager;
        this.onStatusChange = onStatusChange;
        this.getSelected = getSelected;
        this.deselectAll = deselectAll;

        this.myUserId = null;
        this.sync = null;
        this.saveTimer = null;
    }

    /** Подключиться */
    connect() {
        this.sync = new SyncManager(
            `${Config.wsBase}/ws/chunk/${Config.chunkId}/`,
            {
                onWelcome: (data) => this._onWelcome(data),
                onObjectUpdated: (data) => this._onObjectUpdated(data),
                onObjectDeleted: (objectId) => this._onObjectDeleted(objectId),
                onServerIdReceived: (clientId, serverId) => this._onServerIdReceived(clientId, serverId),
                onStatusChange: (text, bg) => this.onStatusChange(text, bg),
            }
        );
        this.sync.connect();

        // Офлайн-фолбек
        setTimeout(() => this._offlineFallback(), 3000);
    }

    /** Отправить создание объекта */
    sendCreate(mesh) {
        if (!mesh?.metadata?.id) return;
        this.sync.sendObjectCreateRaw(
            mesh.metadata.id,
            mesh.metadata,
            mesh.position,
            mesh.rotation,
            mesh.scaling
        );
    }

    /** Отправить обновление объекта (вызывается при каждом движении) */
    sendUpdate(mesh) {
        if (!mesh?.metadata?.id) return;
        this.sync.sendObjectUpdateRaw(
            mesh.metadata.id,
            mesh.position,
            mesh.rotation,
            mesh.scaling,
            mesh.metadata
        );
    }

    /** Отправить удаление объекта */
    sendDelete(id) {
        this.sync.sendObjectDelete(id);
    }

    /** Запланировать сохранение (debounce 2 сек) */
    scheduleSave() {
        clearTimeout(this.saveTimer);
        this.saveTimer = setTimeout(() => this._saveChunk(), 2000);
    }

    // ==================== ПРИВАТНЫЕ ====================

    async _onWelcome(data) {
        this._welcomeReceived = true;
        this.myUserId = data.user_id;
        this.onStatusChange('📂 Загрузка...');

        const saved = await NetworkManager.loadChunk();
        for (const [id, objData] of Object.entries(saved.objects || {})) {
            this.om.createFromData(id, objData);
        }

        const n = Object.keys(saved.objects || {}).length;
        this.onStatusChange(n ? `🟢 ${n} объектов` : '🟢 Новый чанк');
    }

    _onObjectUpdated(data) {
        // Игнорируем свои изменения
        if (data.user_id === this.myUserId) return;

        const id = data.server_id || data.object_id;
        const meta = data.params || {};

        if (!this.om.allObjects[id]) {
            // Новый объект от другого пользователя
            this.om.createFromData(id, {
                position: data.position,
                rotation: data.rotation,
                scale: data.scale,
                params: meta,
                color: meta.color || data.color,
            });
        } else {
            // Обновление существующего
            const mesh = this.om.allObjects[id].mesh;
            if (data.position) mesh.position.set(data.position.x, data.position.y, data.position.z);
            if (data.rotation) mesh.rotation.set(data.rotation.x, data.rotation.y, data.rotation.z);
            if (data.scale) mesh.scaling.set(data.scale.x, data.scale.y, data.scale.z);
        }
    }

    _onObjectDeleted(objectId) {
        const id = objectId.server_id || objectId;
        if (this.om.allObjects[id]) {
            this.om.removeObject(id);

            // Снимаем выделение если удалён выделенный объект
            const selected = this.getSelected();
            if (selected?.metadata?.id === id) {
                this.deselectAll();
            }
        }
    }

    _onServerIdReceived(clientId, serverId) {
        if (this.om.allObjects[clientId]) {
            this.om.allObjects[clientId].mesh.metadata.id = serverId;
            this.om.allObjects[serverId] = this.om.allObjects[clientId];
            delete this.om.allObjects[clientId];
        }
    }

    async _offlineFallback() {
        if (this._welcomeReceived) return;
        // Если через 3 секунды всё ещё «Загрузка...» — пробуем HTTP
        try {
            const saved = await NetworkManager.loadChunk();
            const n = Object.keys(saved.objects || {}).length;
            if (n > 0) {
                for (const [id, data] of Object.entries(saved.objects)) {
                    this.om.createFromData(id, data);
                }
                this.onStatusChange(`🟡 Офлайн | ${n} объектов`);
            } else {
                this.onStatusChange('🟡 Офлайн | Чанк пуст');
            }
        } catch {
            this.onStatusChange('🟡 Нет соединения');
        }
    }

    async _saveChunk() {
        const data = this.om.getAllObjectsData();
        await NetworkManager.saveChunk(data);
        this.onStatusChange('💾 Сохранено');
        setTimeout(() => this.onStatusChange('🟢 Подключено'), 1500);
    }
}