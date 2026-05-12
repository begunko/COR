// static/js/objects/BabylonMeshFactory.js
// ==============================================================================
// ФАБРИКА МЕШЕЙ НА BABYLON.JS
// Принимает JSON-params → возвращает BABYLON.Mesh / TransformNode
// ==============================================================================

import * as BABYLON from '../core/BabylonBridge.js';

let objectCounter = 0;
const DEFAULT_COLOR = '#ff6600';

function hexToColor3(hex) {
    const r = parseInt(hex.slice(1, 3), 16) / 255;
    const g = parseInt(hex.slice(3, 5), 16) / 255;
    const b = parseInt(hex.slice(5, 7), 16) / 255;
    return new BABYLON.Color3(r, g, b);
}

function createPBRMaterial(name, params, scene) {
    const mat = new BABYLON.PBRMaterial(name, scene);
    mat.albedoColor = hexToColor3(params.color || DEFAULT_COLOR);
    mat.roughness = params.roughness ?? 0.3;
    mat.metallic = params.metalness ?? 0.1;

    if (params.wireframe) {
        mat.wireframe = true;
    }

    if ((params.opacity ?? 1) < 1) {
        mat.transparencyMode = BABYLON.PBRMaterial.PBRMATERIAL_ALPHABLEND;
        mat.alpha = params.opacity;
        mat.backFaceCulling = false;
    }

    return mat;
}

const GEOMETRY_MAP = {
    'BoxGeometry': (params, name, scene) => BABYLON.MeshBuilder.CreateBox(name, {
        width: params.width || params.size || 1,
        height: params.height || params.size || 1,
        depth: params.depth || params.size || 1,
    }, scene),

    'SphereGeometry': (params, name, scene) => BABYLON.MeshBuilder.CreateSphere(name, {
        diameter: (params.radius || 0.5) * 2,
        segments: params.widthSegments || 32,
    }, scene),

    'CylinderGeometry': (params, name, scene) => BABYLON.MeshBuilder.CreateCylinder(name, {
        height: params.height || 1,
        diameterTop: (params.radiusTop ?? params.radius ?? 0.5) * 2,
        diameterBottom: (params.radiusBottom ?? params.radius ?? 0.5) * 2,
        tessellation: params.segments || 32,
    }, scene),

    'ConeGeometry': (params, name, scene) => BABYLON.MeshBuilder.CreateCylinder(name, {
        height: params.height || 1,
        diameterTop: 0,
        diameterBottom: (params.radius || 0.5) * 2,
        tessellation: params.segments || 32,
    }, scene),

    'PlaneGeometry': (params, name, scene) => BABYLON.MeshBuilder.CreatePlane(name, {
        width: params.width || 5,
        height: params.height || 5,
    }, scene),

    'TorusGeometry': (params, name, scene) => BABYLON.MeshBuilder.CreateTorus(name, {
        diameter: (params.radius || 1) * 2,
        thickness: (params.tube || 0.3) * 2,
        tessellation: params.tubularSegments || 32,
    }, scene),

    'CapsuleGeometry': (params, name, scene) => BABYLON.MeshBuilder.CreateCapsule(name, {
        radius: params.radius || 0.3,
        height: params.length || 1,
        tessellation: params.segments || 32,
    }, scene),

    'TetrahedronGeometry': (params, name, scene) => BABYLON.MeshBuilder.CreatePolyhedron(name, {
        type: BABYLON.Mesh.TETRAHEDRON,
        size: params.radius || 0.7,
    }, scene),

    'OctahedronGeometry': (params, name, scene) => BABYLON.MeshBuilder.CreatePolyhedron(name, {
        type: BABYLON.Mesh.OCTAHEDRON,
        size: params.radius || 0.7,
    }, scene),

    'IcosahedronGeometry': (params, name, scene) => BABYLON.MeshBuilder.CreatePolyhedron(name, {
        type: BABYLON.Mesh.ICOSAHEDRON,
        size: params.radius || 0.7,
    }, scene),

    'DodecahedronGeometry': (params, name, scene) => BABYLON.MeshBuilder.CreatePolyhedron(name, {
        type: BABYLON.Mesh.DODECAHEDRON,
        size: params.radius || 0.7,
    }, scene),

    'TorusKnotGeometry': (params, name, scene) => BABYLON.MeshBuilder.CreateTorusKnot(name, {
        radius: params.radius || 0.8,
        tube: params.tube || 0.2,
        radialSegments: params.radialSegments || 8,
        tubularSegments: params.tubularSegments || 64,
        p: params.p || 2,
        q: params.q || 3,
    }, scene),

    'CircleGeometry': (params, name, scene) => BABYLON.MeshBuilder.CreateDisc(name, {
        radius: params.radius || 1,
        tessellation: params.segments || 32,
    }, scene),
};

/**
 * Создаёт меш или группу из параметров
 */
export function createMeshFromParams(params = {}, scene, position = null) {
    const geometryName = params.geometry || 'BoxGeometry';

    // ===== ГРУППА =====
    if (geometryName === 'Group') {
        return createGroupFromParams(params, scene, position);
    }

    // ===== ОДИНОЧНЫЙ МЕШ =====
    const constructor = GEOMETRY_MAP[geometryName];
    let mesh;

    if (constructor) {
        mesh = constructor(params, params.name || 'mesh', scene);
    } else {
        console.warn(`Неизвестная геометрия: ${geometryName}, создаю Box`);
        mesh = BABYLON.MeshBuilder.CreateBox(params.name || 'fallback', {
            width: 1, height: 1, depth: 1,
        }, scene);
    }

    // Материал
    mesh.material = createPBRMaterial('mat_' + (params.name || 'obj'), params, scene);
    mesh.receiveShadows = true;

    // Позиция
    if (position) {
        mesh.position.copyFrom(position);
    } else if (params.position) {
        mesh.position.set(
            params.position[0] || 0,
            params.position[1] || params.defaultY || 0.5,
            params.position[2] || 0
        );
    } else {
        mesh.position.set(
            (Math.random() - 0.5) * 6,
            params.defaultY || 1,
            (Math.random() - 0.5) * 6
        );
    }

    // Поворот
    if (params.rotation) {
        mesh.rotation.set(
            params.rotation[0] || 0,
            params.rotation[1] || 0,
            params.rotation[2] || 0
        );
    }

    // Масштаб
    if (params.scale) {
        mesh.scaling.set(
            params.scale[0] || 1,
            params.scale[1] || 1,
            params.scale[2] || 1
        );
    }

    // Метаданные
    objectCounter++;
    mesh.metadata = {
        id: `obj-${objectCounter}-${Date.now()}`,
        geometry: geometryName,
        params: { ...params },
    };

    // Доступность для кликов
    mesh.isPickable = true;

    return mesh;
}

/** Создаёт группу из params.children */
function createGroupFromParams(params, scene, position) {
    const group = new BABYLON.TransformNode(params.name || 'group', scene);
    const children = params.children || [];

    children.forEach(childParams => {
        const child = createMeshFromParams(
            { ...childParams, geometry: childParams.geometry || 'BoxGeometry' },
            scene
        );
        child.setParent(group);

        if (childParams.position) {
            child.position.set(
                childParams.position[0] || 0,
                childParams.position[1] || 0,
                childParams.position[2] || 0
            );
        }
        if (childParams.rotation) {
            child.rotation.set(
                childParams.rotation[0] || 0,
                childParams.rotation[1] || 0,
                childParams.rotation[2] || 0
            );
        }
        if (childParams.scale_override) {
            child.scaling.set(
                childParams.scale_override[0] || 1,
                childParams.scale_override[1] || 1,
                childParams.scale_override[2] || 1
            );
        }
    });

    if (position) {
        group.position.copyFrom(position);
    } else {
        group.position.set(
            (Math.random() - 0.5) * 6,
            params.defaultY || 1,
            (Math.random() - 0.5) * 6
        );
    }

    objectCounter++;
    group.metadata = {
        id: `group-${objectCounter}-${Date.now()}`,
        geometry: 'Group',
        params: { ...params },
    };

    return group;
}

export { GEOMETRY_MAP };