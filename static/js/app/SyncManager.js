// static/js/app/SyncManager.js
import { WebSocketClient } from '../core/WebSocketClient.js';

export class SyncManager {
    constructor(wsUrl, callbacks = {}) {
        this.callbacks = callbacks;
        this.myUserId = null;
        this.myColor = null;
        // Маппинг client_id -> server_id
        this.idMapping = {};

        this.wsClient = new WebSocketClient(wsUrl, {
            onOpen: () => this._setStatus('🟢 Подключено', 'rgba(0, 150, 0, 0.75)'),
            onMessage: (data) => this._handleMessage(data),
            onClose: () => this._setStatus('🔴 Соединение потеряно', 'rgba(200, 0, 0, 0.75)'),
            onError: () => this._setStatus('⚠️ Ошибка WebSocket', 'rgba(200, 100, 0, 0.75)'),
        });
    }

    connect() {
        this.wsClient.connect();
    }

    isConnected() {
        return this.wsClient.isConnected();
    }

    sendObjectUpdate(object) {
        if (!this.wsClient.isConnected()) return;
        const params = object.userData.params || {};
        // Используем server_id если есть, иначе client_id
        const serverId = object.userData.serverId || object.userData.id;
        this.wsClient.send({
            type: 'object_updated',
            server_id: serverId,
            object_type: object.userData.type || 'mesh',
            color: object.userData.color || params.color || '#ff6600',
            params: params,
            position: {
                x: +object.position.x.toFixed(3),
                y: +object.position.y.toFixed(3),
                z: +object.position.z.toFixed(3),
            },
            rotation: {
                x: +object.rotation.x.toFixed(3),
                y: +object.rotation.y.toFixed(3),
                z: +object.rotation.z.toFixed(3),
            },
            scale: {
                x: +object.scale.x.toFixed(3),
                y: +object.scale.y.toFixed(3),
                z: +object.scale.z.toFixed(3),
            },
        });
    }

    sendObjectCreate(object, params) {
        if (!this.wsClient.isConnected()) return;
        this.wsClient.send({
            type: 'object_create',
            client_id: object.userData.id,  // временный ID клиента
            object_type: 'mesh',
            color: params.color || '#ff6600',
            params: params,
            position: {
                x: +object.position.x.toFixed(3),
                y: +object.position.y.toFixed(3),
                z: +object.position.z.toFixed(3),
            },
            rotation: {
                x: +object.rotation.x.toFixed(3),
                y: +object.rotation.y.toFixed(3),
                z: +object.rotation.z.toFixed(3),
            },
            scale: {
                x: +object.scale.x.toFixed(3),
                y: +object.scale.y.toFixed(3),
                z: +object.scale.z.toFixed(3),
            },
        });
    }

    sendObjectDelete(objectId) {
        if (!this.wsClient.isConnected()) return;
        this.wsClient.send({
            type: 'object_delete',
            server_id: objectId,
        });
    }

    _handleMessage(data) {
        // welcome
        if (data.type === 'welcome') {
            this.myUserId = data.user_id;
            this.myColor = data.color;
            if (this.callbacks.onWelcome) {
                this.callbacks.onWelcome(data);
            }
        }

        // object_created — подтверждение от сервера с server_id
        if (data.type === 'object_created') {
            // Сохраняем маппинг
            if (data.client_id && data.server_id) {
                this.idMapping[data.client_id] = data.server_id;
            }

            const params = data.params || {};
            if (this.callbacks.onObjectUpdated) {
                this.callbacks.onObjectUpdated(data, params);
            }

            this._setStatus('✅ Объект создан', 'rgba(0, 150, 0, 0.75)');
            setTimeout(() => this._setStatus('🟢 Подключено', 'rgba(0, 150, 0, 0.75)'), 2000);
        }

        // object_updated — от других пользователей
        if (data.type === 'object_updated' && data.user_id !== this.myUserId) {
            const params = data.params || {};
            if (this.callbacks.onObjectUpdated) {
                this.callbacks.onObjectUpdated(data, params);
            }

            this._setStatus('🔄 Объект обновлён', 'rgba(0, 100, 200, 0.75)');
            setTimeout(() => this._setStatus('🟢 Подключено', 'rgba(0, 150, 0, 0.75)'), 2000);
        }

        // object_deleted
        if (data.type === 'object_deleted') {
            const objId = data.server_id || data.object_id;
            if (this.callbacks.onObjectDeleted) {
                this.callbacks.onObjectDeleted(objId);
            }
            this._setStatus('🗑 Объект удалён', 'rgba(200, 0, 0, 0.75)');
            setTimeout(() => this._setStatus('🟢 Подключено'), 2000);
        }

        // user_left
        if (data.type === 'user_left') {
            if (this.callbacks.onUserLeft) {
                this.callbacks.onUserLeft(data);
            }
        }
    }

    _setStatus(text, bg) {
        if (this.callbacks.onStatusChange) {
            this.callbacks.onStatusChange(text, bg);
        }
    }

    async saveToServer(chunkId, objectsData) {
        try {
            const urlParams = new URLSearchParams(window.location.search);
            const worldId = urlParams.get('world_id');

            // Конвертируем client_id в server_id для сохранения
            const convertedData = {};
            for (const [id, objData] of Object.entries(objectsData)) {
                const serverId = this.idMapping[id] || id;
                convertedData[serverId] = objData;
            }

            const body = {
                objects: convertedData,
                chunk_type: 'full'
            };
            if (worldId) body.world_id = worldId;

            const response = await fetch(`/api/chunk/${chunkId}/save/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body),
            });
            const result = await response.json();
            console.log('💾 Чанк сохранён:', result);
            return result;
        } catch (error) {
            console.error('❌ Ошибка сохранения чанка:', error);
            return null;
        }
    }

    async loadFromServer(chunkId) {
        try {
            const response = await fetch(`/api/chunk/${chunkId}/load/`);
            const data = await response.json();
            console.log('📂 Чанк загружен:', data);
            return data;
        } catch (error) {
            console.error('❌ Ошибка загрузки чанка:', error);
            return { objects: {}, chunk_type: 'void' };
        }
    }
}