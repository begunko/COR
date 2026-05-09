import * as THREE from 'three';

let objectCounter = 0;
const DEFAULT_COLOR = '#ff6600';

/**
 * Универсальная фабрика 3D-объектов.
 * Принимает params из API (default_params инструмента) и создаёт меш.
 */
export function createMeshFromParams(params = {}, position = null) {
    const meshType = params.mesh_type || 'cube';
    let geometry;

    switch (meshType) {
        case 'cube':
        case 'box':
            const size = params.size || 1;
            geometry = new THREE.BoxGeometry(size, size, size);
            break;

        case 'sphere':
            const radius = params.radius || 0.5;
            const sphereSegments = params.segments || 32;
            geometry = new THREE.SphereGeometry(radius, sphereSegments, sphereSegments);
            break;

        case 'cylinder':
            const cylRadius = params.radius || 0.5;
            const cylHeight = params.height || 1;
            const cylSegments = params.segments || 32;
            geometry = new THREE.CylinderGeometry(cylRadius, cylRadius, cylHeight, cylSegments);
            break;

        case 'cone':
            const coneRadius = params.radius || 0.5;
            const coneHeight = params.height || 1;
            const coneSides = params.sides || 6;
            geometry = new THREE.CylinderGeometry(0, coneRadius, coneHeight, coneSides);
            break;

        case 'pyramid':
            const pyrSize = params.size || 1;
            const pyrHeight = params.height || 1;
            geometry = new THREE.ConeGeometry(pyrSize, pyrHeight, 4);
            break;

        case 'plane':
            const planeWidth = params.width || 5;
            const planeHeight = params.height || 5;
            geometry = new THREE.PlaneGeometry(planeWidth, planeHeight);
            break;

        case 'torus':
            const torusRadius = params.radius || 1;
            const tubeRadius = params.tube || 0.3;
            geometry = new THREE.TorusGeometry(torusRadius, tubeRadius, 16, 32);
            break;

        default:
            // По умолчанию — куб
            geometry = new THREE.BoxGeometry(1, 1, 1);
    }

    // Материал
    const color = params.color || DEFAULT_COLOR;
    const roughness = params.roughness ?? 0.3;
    const metalness = params.metalness ?? 0.1;
    const material = new THREE.MeshStandardMaterial({ color, roughness, metalness });

    // Меш
    const mesh = new THREE.Mesh(geometry, material);
    mesh.castShadow = true;
    mesh.receiveShadow = true;

    // Уникальный ID
    objectCounter++;
    mesh.userData = {
        id: `obj-${objectCounter}-${Date.now()}`,
        color: color,
        type: meshType,
        params: params
    };

    // Позиция
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