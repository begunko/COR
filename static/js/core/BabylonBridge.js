// static/js/core/BabylonBridge.js
const B = window.BABYLON;
if (!B) console.error('❌ BABYLON не загружен!');

export const Engine = B?.Engine;
export const Scene = B?.Scene;
export const ArcRotateCamera = B?.ArcRotateCamera;
export const HemisphericLight = B?.HemisphericLight;
export const DirectionalLight = B?.DirectionalLight;
export const Vector3 = B?.Vector3;
export const Color3 = B?.Color3;
export const Color4 = B?.Color4;
export const MeshBuilder = B?.MeshBuilder;
export const PBRMaterial = B?.PBRMaterial;
export const GridMaterial = B?.GridMaterial;
export const GizmoManager = B?.GizmoManager;
export const PointerDragBehavior = B?.PointerDragBehavior;
export const PointerEventTypes = B?.PointerEventTypes;
export const ShadowGenerator = B?.ShadowGenerator;
export const TransformNode = B?.TransformNode;
export const AbstractMesh = B?.AbstractMesh;
export const Mesh = B?.Mesh;
export const GUI = B?.GUI;
export const PointLight = B?.PointLight;
export const SpotLight = B?.SpotLight;

export default B;