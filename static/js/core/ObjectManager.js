// static/js/core/ObjectManager.js
// ==============================================================================
// МЕНЕДЖЕР ОБЪЕКТОВ — создание, удаление, обновление объектов сцены
// ==============================================================================

import * as BABYLON from './BabylonBridge.js';

export class ObjectManager {
    constructor(scene, shadowGenerator) {
        this.scene = scene;
        this.shadowGenerator = shadowGenerator;
        this.allObjects = {};      // { id: { mesh, metadata } }
        this.onObjectChanged = null; // callback(mesh) — вызывается при изменении
    }

    /**
     * Создать объект из геометрии
     */
    createGeometry(geometryName, methodName, params, id = null, color = null, position = null, rotation = null, scale = null) {
        const meshId = id || `${geometryName}-${Date.now()}`;
        const mesh = BABYLON.MeshBuilder[methodName](meshId, params, this.scene);

        // Материал
        if (!mesh.material) {
            mesh.material = new BABYLON.PBRMaterial(`mat_${meshId}`, this.scene);
        }
        const colorHex = color || this._randomColor();
        mesh.material.albedoColor = BABYLON.Color3.FromHexString(colorHex);
        mesh.material.roughness = 0.3;
        mesh.material.metallic = 0.1;

        // Тени
        if (this.shadowGenerator) {
            this.shadowGenerator.addShadowCaster(mesh, true);
            mesh.receiveShadows = true;
        }

        // Трансформация
        if (position) mesh.position.copyFrom(position);
        if (rotation) mesh.rotation.copyFrom(rotation);
        if (scale) mesh.scaling.copyFrom(scale);

        // Метаданные
        mesh.metadata = {
            id: meshId,
            type: 'geometry',
            geometry: geometryName,
            method: methodName,
            params: { ...params },
            color: colorHex,
        };
        mesh.isPickable = true;

        // Drag & Drop
        this._addDragBehavior(mesh);

        this.allObjects[meshId] = { mesh, metadata: mesh.metadata };
        return mesh;
    }

    /**
     * Создать объект из загруженных данных (восстановление после F5)
     */
    createFromData(id, data) {
        const meta = data.params || {};
        const geometry = meta.geometry || data.type || 'Box';
        const method = meta.method || `Create${geometry}`;
        const params = meta.params || { size: 1 };
        const color = meta.color || data.color || '#ff6600';

        const pos = new BABYLON.Vector3(
            data.position?.x || 0,
            data.position?.y || 0,
            data.position?.z || 0
        );
        const rot = data.rotation
            ? new BABYLON.Vector3(data.rotation.x, data.rotation.y, data.rotation.z)
            : null;
        const scl = data.scale
            ? new BABYLON.Vector3(data.scale.x, data.scale.y, data.scale.z)
            : null;

        return this.createGeometry(geometry, method, params, id, color, pos, rot, scl);
    }

    /**
     * Обновить позицию/поворот/масштаб существующего объекта
     */
    updateObject(id, position, rotation, scale) {
        const entry = this.allObjects[id];
        if (!entry) return;

        if (position) entry.mesh.position.copyFrom(position);
        if (rotation) entry.mesh.rotation.copyFrom(rotation);
        if (scale) entry.mesh.scaling.copyFrom(scale);
    }

    /**
     * Удалить объект
     */
    removeObject(id) {
        const entry = this.allObjects[id];
        if (entry) {
            entry.mesh.dispose();
            delete this.allObjects[id];
        }
    }

    /**
     * Получить данные всех объектов для сохранения
     */
    getAllObjectsData() {
        const data = {};
        for (const [id, entry] of Object.entries(this.allObjects)) {
            const m = entry.mesh;
            data[id] = {
                color: m.metadata?.color || '#ff6600',
                position: {
                    x: +m.position.x.toFixed(3),
                    y: +m.position.y.toFixed(3),
                    z: +m.position.z.toFixed(3),
                },
                rotation: {
                    x: +m.rotation.x.toFixed(3),
                    y: +m.rotation.y.toFixed(3),
                    z: +m.rotation.z.toFixed(3),
                },
                scale: {
                    x: +m.scaling.x.toFixed(3),
                    y: +m.scaling.y.toFixed(3),
                    z: +m.scaling.z.toFixed(3),
                },
                type: m.metadata?.geometry || 'Box',
                params: m.metadata || {},
            };
        }
        return data;
    }

    /**
     * Экспорт для синхронизации
     */
    getSyncData(mesh) {
        return {
            id: mesh.metadata?.id,
            position: mesh.position,
            rotation: mesh.rotation,
            scale: mesh.scaling,
            metadata: mesh.metadata,
        };
    }

    // ==================== ПРИВАТНЫЕ ====================

    _addDragBehavior(mesh) {
        const drag = new BABYLON.PointerDragBehavior({
            dragPlaneNormal: new BABYLON.Vector3(0, 1, 0),
        });
        drag.moveAttached = false;
        mesh.addBehavior(drag);

        // Непрерывная отправка во время перетаскивания
        drag.onDragObservable.add(() => {
            if (this.onObjectChanged) this.onObjectChanged(mesh);
        });

        drag.onDragEndObservable.add(() => {
            if (this.onObjectChanged) this.onObjectChanged(mesh);
        });
    }

    _randomColor() {
        const h = Math.floor(Math.random() * 360);
        const s = 0.5 + Math.random() * 0.4;
        const l = 0.4 + Math.random() * 0.3;
        return this._hslToHex(h, s, l);
    }

    _hslToHex(h, s, l) {
        const a = s * Math.min(l, 1 - l);
        const f = n => {
            const k = (n + h / 30) % 12;
            return l - a * Math.max(Math.min(k - 3, 9 - k, 1), -1);
        };
        const toHex = x => Math.round(x * 255).toString(16).padStart(2, '0');
        return `#${toHex(f(0))}${toHex(f(8))}${toHex(f(4))}`;
    }
}