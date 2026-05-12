/**
 * ================================================================
 * COR ENGINE — Admin Panel Logic
 * ================================================================
 */

'use strict';

document.addEventListener('DOMContentLoaded', () => {
    console.log('💻 COR Admin Panel v1.0');
    highlightActiveSidebar();
});

/**
 * Подсветка активного пункта в сайдбаре
 */
function highlightActiveSidebar() {
    const currentPath = window.location.pathname;

    document.querySelectorAll('.cor-sidebar-item').forEach(item => {
        const href = item.getAttribute('href');
        if (href && currentPath.startsWith(href)) {
            item.classList.add('active');
        }
    });
}