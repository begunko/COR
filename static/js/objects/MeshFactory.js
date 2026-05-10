import * as THREE from 'three';

let objectCounter = 0;
const DEFAULT_COLOR = '#ff6600';

// Словарь конструкторов Three.js
const GEOMETRY_CONSTRUCTORS = {
    // Базовые
    'BoxGeometry': (p) => [p.width || p.size || 1, p.height || p.size || 1, p.depth || p.size || 1],
    'SphereGeometry': (p) => [p.radius || 0.5, p.widthSegments || 32, p.heightSegments || 32],
    'CylinderGeometry': (p) => [p.radiusTop ?? p.radius ?? 0.5, p.radiusBottom ?? p.radius ?? 0.5, p.height || 1, p.segments || 32],
    'ConeGeometry': (p) => [p.radius || 0.5, p.height || 1, p.segments || 32],
    'PlaneGeometry': (p) => [p.width || 5, p.height || 5],
    'TorusGeometry': (p) => [p.radius || 1, p.tube || 0.3, p.radialSegments || 16, p.tubularSegments || 32],
    // Платоновы тела
    'TetrahedronGeometry': (p) => [p.radius || 0.7],
    'OctahedronGeometry': (p) => [p.radius || 0.7],
    'IcosahedronGeometry': (p) => [p.radius || 0.7],
    'DodecahedronGeometry': (p) => [p.radius || 0.7],
    // Экзотические
    'TorusKnotGeometry': (p) => [p.radius || 0.8, p.tube || 0.2, p.tubularSegments || 64, p.radialSegments || 8, p.p || 2, p.q || 3],
    'RingGeometry': (p) => [p.innerRadius || 0.5, p.outerRadius || 1, p.segments || 32],
    'CircleGeometry': (p) => [p.radius || 1, p.segments || 32],
    'CapsuleGeometry': (p) => [p.radius || 0.3, p.length || 1, p.segments || 32, p.radiusSegments || 32],
};

/**
 * Универсальная фабрика 3D-объектов.
 * Принимает params с полем 'geometry' (имя конструктора Three.js) и параметрами.
 * 
 * Пример params:
 * {
 *   geometry: 'BoxGeometry',
 *   width: 1, height: 2, depth: 0.5,
 *   color: '#ff6600',
 *   roughness: 0.3,
 *   metalness: 0.1,
 *   wireframe: false,
 *   opacity: 1.0,
 *   defaultY: 0.5
 * }
 */
export function createMeshFromParams(params = {}, position = null) {
    const geometryName = params.geometry || 'BoxGeometry';

    let geometry;

    if (geometryName === 'lathe' || geometryName === 'LatheGeometry') {
        // Особая обработка для тела вращения
        const points = createLatheProfile(params.profile || 'vase');
        geometry = new THREE.LatheGeometry(points, params.segments || 32);
    } else if (geometryName === 'shape' || geometryName === 'ShapeGeometry') {
        // Особая обработка для Shape
        geometry = createShapeGeometry(params);
    } else if (GEOMETRY_CONSTRUCTORS[geometryName]) {
        // Стандартные фигуры
        const args = GEOMETRY_CONSTRUCTORS[geometryName](params);
        const Constructor = THREE[geometryName];
        geometry = new Constructor(...args);
    } else {
        // Fallback — куб
        console.warn(`Unknown geometry: ${geometryName}, using BoxGeometry`);
        geometry = new THREE.BoxGeometry(1, 1, 1);
    }

    // Материал — тоже из params
    const materialParams = {
        color: params.color || DEFAULT_COLOR,
        roughness: params.roughness ?? 0.3,
        metalness: params.metalness ?? 0.1,
        wireframe: params.wireframe || false,
        transparent: (params.opacity ?? 1) < 1,
        opacity: params.opacity ?? 1,
    };
    const material = new THREE.MeshStandardMaterial(materialParams);

    const mesh = new THREE.Mesh(geometry, material);
    mesh.castShadow = true;
    mesh.receiveShadow = true;

    objectCounter++;
    mesh.userData = {
        id: `obj-${objectCounter}-${Date.now()}`,
        geometry: geometryName,
        material: materialParams,
        params: params
    };

    if (position) {
        mesh.position.set(position.x, position.y, position.z);
    } else {
        mesh.position.set(
            (Math.random() - 0.5) * 6,
            (params.defaultY || 1),
            (Math.random() - 0.5) * 6
        );
    }

    return mesh;
}

function createLatheProfile(profileName) {
    if (profileName === 'vase') {
        return [
            [0, -0.5], [0.3, -0.4], [0.5, -0.2], [0.4, 0],
            [0.2, 0.2], [0.1, 0.3], [0.15, 0.45], [0.2, 0.5]
        ].map(p => new THREE.Vector2(p[0], p[1]));
    }
    if (profileName === 'egg') {
        const pts = [];
        for (let i = 0; i <= 20; i++) {
            const t = i / 20;
            pts.push(new THREE.Vector2(Math.sin(t * Math.PI) * 0.4, t - 0.5));
        }
        return pts;
    }
    return [new THREE.Vector2(0, -0.5), new THREE.Vector2(0.4, 0.5)];
}

function createShapeGeometry(params) {
    const shapeType = params.shape || 'heart';
    const shape = new THREE.Shape();

    if (shapeType === 'heart') {
        shape.moveTo(0, 0.3);
        shape.bezierCurveTo(0, 0.6, 0.5, 0.8, 0.5, 0.5);
        shape.bezierCurveTo(0.5, 0.8, 1, 0.6, 1, 0.3);
        shape.bezierCurveTo(1, -0.3, 0.5, -0.5, 0.5, -0.5);
        shape.bezierCurveTo(0.5, -0.5, 0, -0.3, 0, 0.3);
    } else if (shapeType === 'star') {
        const outerR = 0.6, innerR = 0.25, numPoints = 5;
        for (let i = 0; i < numPoints * 2; i++) {
            const r = i % 2 === 0 ? outerR : innerR;
            const angle = (i / (numPoints * 2)) * Math.PI * 2 - Math.PI / 2;
            if (i === 0) shape.moveTo(Math.cos(angle) * r, Math.sin(angle) * r);
            else shape.lineTo(Math.cos(angle) * r, Math.sin(angle) * r);
        }
        shape.closePath();
    }

    return new THREE.ExtrudeGeometry(shape, {
        depth: params.extrudeDepth || 0.2,
        bevelEnabled: true,
        bevelThickness: params.bevelThickness || 0.05,
        bevelSize: params.bevelSize || 0.05,
        bevelSegments: 3
    });
}