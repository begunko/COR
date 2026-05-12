// static/js/app/SyncManager.js
import { WebSocketClient } from './WebSocketClient.js';

export class SyncManager {
    constructor(wsUrl, callbacks = {}) {
        this.callbacks = callbacks;
        this.myUserId = null;
        this.myColor = null;
        this.idMapping = {};
        this.myPendingCreates = new Set();

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

    // Универсальный метод обновления
    sendObjectUpdateRaw(objectId, position, rotation, scale, params) {
        if (!this.wsClient.isConnected()) return;
        this.wsClient.send({
            type: 'object_updated',
            server_id: objectId,
            position: {
                x: +position.x.toFixed(3),
                y: +position.y.toFixed(3),
                z: +position.z.toFixed(3),
            },
            rotation: {
                x: +(rotation?.x || 0).toFixed(3),
                y: +(rotation?.y || 0).toFixed(3),
                z: +(rotation?.z || 0).toFixed(3),
            },
            scale: {
                x: +(scale?.x || 1).toFixed(3),
                y: +(scale?.y || 1).toFixed(3),
                z: +(scale?.z || 1).toFixed(3),
            },
            params: params || {},
        });
    }

    // Универсальный метод создания
    sendObjectCreateRaw(clientId, params, position, rotation, scale) {
        if (!this.wsClient.isConnected()) return;
        this.myPendingCreates.add(clientId);
        this.wsClient.send({
            type: 'object_create',
            client_id: clientId,
            object_type: params.geometry === 'Group' ? 'group' : 'mesh',
            color: params.color || '#ff6600',
            params: params,
            position: {
                x: +position.x.toFixed(3),
                y: +position.y.toFixed(3),
                z: +position.z.toFixed(3),
            },
            rotation: {
                x: +(rotation?.x || 0).toFixed(3),
                y: +(rotation?.y || 0).toFixed(3),
                z: +(rotation?.z || 0).toFixed(3),
            },
            scale: {
                x: +(scale?.x || 1).toFixed(3),
                y: +(scale?.y || 1).toFixed(3),
                z: +(scale?.z || 1).toFixed(3),
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
        if (data.type === 'welcome') {
            this.myUserId = data.user_id;
            this.myColor = data.color;
            if (this.callbacks.onWelcome) {
                this.callbacks.onWelcome(data);
            }
        }

        if (data.type === 'object_created') {
            if (data.client_id && this.myPendingCreates.has(data.client_id)) {
                this.myPendingCreates.delete(data.client_id);
                if (data.server_id) {
                    this.idMapping[data.client_id] = data.server_id;
                    if (this.callbacks.onServerIdReceived) {
                        this.callbacks.onServerIdReceived(data.client_id, data.server_id);
                    }
                }
                return;
            }

            if (data.client_id && data.server_id) {
                this.idMapping[data.client_id] = data.server_id;
            }

            if (this.callbacks.onObjectUpdated) {
                this.callbacks.onObjectUpdated(data);
            }
        }

        if (data.type === 'object_updated' && data.user_id !== this.myUserId) {
            if (this.callbacks.onObjectUpdated) {
                this.callbacks.onObjectUpdated(data);
            }
        }

        if (data.type === 'object_deleted') {
            const objId = data.server_id || data.object_id;
            if (this.callbacks.onObjectDeleted) {
                this.callbacks.onObjectDeleted(objId);
            }
        }

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
}