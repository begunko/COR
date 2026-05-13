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

        // Проверяем, существует ли метод
        if (typeof BABYLON.MeshBuilder[methodName] !== 'function') {
            console.warn(`⚠️ Метод ${methodName} не найден. Создаю Box вместо ${geometryName}.`);
            geometryName = 'Box';
            methodName = 'CreateBox';
            params = { size: 1 };
        }

        let mesh;
        try {
            mesh = BABYLON.MeshBuilder[methodName](meshId, params, this.scene);
        } catch (err) {
            console.error(`❌ Ошибка создания ${geometryName}:`, err);
            // Создаём куб как fallback
            mesh = BABYLON.MeshBuilder.CreateBox(meshId, { size: 1 }, this.scene);
        }

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
        if (!data) {
            console.warn('⚠️ createFromData: нет данных для', id);
            return null;
        }

        const meta = data.params || {};
        // Определяем геометрию и метод
        let geometry = meta.geometry || data.type || 'BoxGeometry';
        let method = meta.method || data.method || `Create${geometry.replace('Geometry', '')}`;

        // Если geometry содержит "Group" — создаём TransformNode
        if (geometry === 'Group' || geometry.includes('Group')) {
            console.log(`📁 Создаю группу: ${id}`);
            return this._createGroupFromData(id, data);
        }

        // Проверяем, существует ли метод в MeshBuilder
        if (typeof BABYLON.MeshBuilder[method] !== 'function') {
            // Пробуем альтернативные названия
            const alternatives = [
                `Create${geometry.replace('Geometry', '')}`,
                `Create${geometry}`,
                'CreateBox'
            ];

            let found = false;
            for (const alt of alternatives) {
                if (typeof BABYLON.MeshBuilder[alt] === 'function') {
                    method = alt;
                    found = true;
                    break;
                }
            }

            if (!found) {
                console.warn(`⚠️ Метод ${method} не найден для ${geometry}. Создаю Box.`);
                geometry = 'BoxGeometry';
                method = 'CreateBox';
            }
        }

        // Параметры для геометрии
        let params = meta.params || {};
        if (!params.size && !params.width && !params.height && !params.diameter && !params.radius) {
            params = { size: 1 }; // дефолтный размер
        }

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
     * Создать группу (TransformNode) из данных
     * @private
     */
    _createGroupFromData(id, data) {
        const meta = data.params || {};
        const group = new BABYLON.TransformNode(id, this.scene);

        const pos = data.position
            ? new BABYLON.Vector3(data.position.x, data.position.y, data.position.z)
            : new BABYLON.Vector3(0, 0, 0);
        group.position = pos;

        group.metadata = {
            id: id,
            type: 'group',
            geometry: 'Group',
            params: { ...meta },
            color: meta.color || data.color || '#ff6600',
        };

        // Создаём дочерние элементы, если есть
        const children = meta.children || [];
        children.forEach((childData, index) => {
            const childId = `${id}_child_${index}`;
            const child = this.createFromData(childId, {
                position: childData.position
                    ? { x: childData.position[0] || 0, y: childData.position[1] || 0, z: childData.position[2] || 0 }
                    : { x: 0, y: 0, z: 0 },
                rotation: childData.rotation
                    ? { x: childData.rotation[0] || 0, y: childData.rotation[1] || 0, z: childData.rotation[2] || 0 }
                    : { x: 0, y: 0, z: 0 },
                scale: childData.scale
                    ? { x: childData.scale[0] || 1, y: childData.scale[1] || 1, z: childData.scale[2] || 1 }
                    : { x: 1, y: 1, z: 1 },
                params: childData,
                color: childData.color || '#ff6600',
            });

            if (child) {
                child.setParent(group);
            }
        });

        this.allObjects[id] = { mesh: group, metadata: group.metadata };
        return group;
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
        try {
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
        } catch (err) {
            console.warn('⚠️ Не удалось добавить DragBehavior:', err.message);
        }
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