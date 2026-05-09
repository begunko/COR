import * as THREE from 'three';

export function createCursor(color = '#ffffff') {
    const geometry = new THREE.SphereGeometry(0.15, 16, 16);
    const material = new THREE.MeshBasicMaterial({ color });
    const cursor = new THREE.Mesh(geometry, material);
    cursor.position.set(0, -10, 0);  // Скрыт под полом по умолчанию
    cursor.userData = { type: 'cursor' };
    return cursor;
}