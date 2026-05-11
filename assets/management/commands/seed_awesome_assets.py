# assets/management/commands/seed_awesome_assets.py
# ==============================================================================
# ПОСЕВ КРУТЫХ АССЕТОВ — готовые композиции для вдохновения
# Запуск: python manage.py seed_awesome_assets
# ==============================================================================

from django.core.management.base import BaseCommand
from assets.models import Asset
from users.models import User

AWESOME_ASSETS = [
    # ================================================================
    # 1. ДРЕВНИЙ ДУБ (эпическое дерево)
    # ================================================================
    {
        "name": "🌳 Древний дуб",
        "description": "Вековой дуб с раскидистой кроной и массивным стволом",
        "tags": ["дерево", "природа", "лес", "эпический"],
        "data": {
            "children": [
                # Массивный ствол
                {
                    "name": "ствол",
                    "geometry": "CylinderGeometry",
                    "color": "#4a3728",
                    "position": [0, 0.8, 0],
                    "scale": [0.5, 1.6, 0.5],
                    "material": {"roughness": 0.9, "metalness": 0.0},
                },
                {
                    "name": "корень_л",
                    "geometry": "CylinderGeometry",
                    "color": "#3d2e1f",
                    "position": [-0.6, 0.1, 0.3],
                    "rotation": [0.4, 0, 0.3],
                    "scale": [0.2, 0.5, 0.2],
                    "material": {"roughness": 0.95},
                },
                {
                    "name": "корень_п",
                    "geometry": "CylinderGeometry",
                    "color": "#3d2e1f",
                    "position": [0.5, 0.1, -0.2],
                    "rotation": [0.3, 0, -0.4],
                    "scale": [0.2, 0.5, 0.2],
                    "material": {"roughness": 0.95},
                },
                # Крона — несколько сфер разного размера
                {
                    "name": "крона_центр",
                    "geometry": "SphereGeometry",
                    "color": "#2d5a1e",
                    "position": [0, 2.5, 0],
                    "scale": [1.2, 0.9, 1.2],
                    "material": {"roughness": 0.8, "metalness": 0.0},
                },
                {
                    "name": "крона_л",
                    "geometry": "SphereGeometry",
                    "color": "#3a6b2a",
                    "position": [-0.8, 2.2, 0.3],
                    "scale": [0.9, 0.7, 0.9],
                    "material": {"roughness": 0.8},
                },
                {
                    "name": "крона_п",
                    "geometry": "SphereGeometry",
                    "color": "#3a6b2a",
                    "position": [0.7, 2.3, -0.4],
                    "scale": [0.85, 0.7, 0.85],
                    "material": {"roughness": 0.8},
                },
                {
                    "name": "крона_верх",
                    "geometry": "SphereGeometry",
                    "color": "#4a8a35",
                    "position": [0.1, 3.0, 0.1],
                    "scale": [0.7, 0.6, 0.7],
                    "material": {"roughness": 0.75},
                },
                {
                    "name": "крона_тыл",
                    "geometry": "SphereGeometry",
                    "color": "#2d5a1e",
                    "position": [0, 2.1, -0.7],
                    "scale": [0.8, 0.65, 0.8],
                    "material": {"roughness": 0.8},
                },
            ]
        },
        "animation": {
            "type": "sway",
            "target": "self",
            "params": {"amplitude": 0.15, "speed": 0.3},
        },
    },
    # ================================================================
    # 2. МАГИЧЕСКИЙ КРИСТАЛЛ НА ПЬЕДЕСТАЛЕ
    # ================================================================
    {
        "name": "💎 Магический кристалл",
        "description": "Светящийся кристалл на каменном пьедестале с рунами",
        "tags": ["магия", "кристалл", "фэнтези", "алтарь"],
        "data": {
            "children": [
                # Пьедестал
                {
                    "name": "база",
                    "geometry": "CylinderGeometry",
                    "color": "#4a4a4a",
                    "position": [0, 0.15, 0],
                    "scale": [1.0, 0.3, 1.0],
                    "material": {"roughness": 0.6, "metalness": 0.3},
                },
                {
                    "name": "колонна",
                    "geometry": "CylinderGeometry",
                    "color": "#5a5a5a",
                    "position": [0, 0.6, 0],
                    "scale": [0.6, 0.8, 0.6],
                    "material": {"roughness": 0.5, "metalness": 0.4},
                },
                {
                    "name": "верх_пьедестала",
                    "geometry": "CylinderGeometry",
                    "color": "#3a3a3a",
                    "position": [0, 1.1, 0],
                    "scale": [0.8, 0.2, 0.8],
                    "material": {"roughness": 0.5, "metalness": 0.5},
                },
                # Кристалл
                {
                    "name": "кристалл_главный",
                    "geometry": "OctahedronGeometry",
                    "color": "#8844ff",
                    "position": [0, 1.8, 0],
                    "scale": [0.5, 0.8, 0.5],
                    "material": {
                        "roughness": 0.05,
                        "metalness": 0.9,
                        "opacity": 0.7,
                        "transparent": True,
                    },
                },
                # Свечение
                {
                    "name": "свечение",
                    "geometry": "SphereGeometry",
                    "color": "#ffffff",
                    "position": [0, 1.8, 0],
                    "scale": [0.3, 0.3, 0.3],
                    "material": {
                        "roughness": 0.1,
                        "metalness": 0.0,
                        "opacity": 0.6,
                        "transparent": True,
                    },
                },
                # Руны (маленькие кубики вокруг)
                {
                    "name": "руна_1",
                    "geometry": "BoxGeometry",
                    "color": "#ffdd00",
                    "position": [0.5, 0.9, 0.5],
                    "scale": [0.1, 0.05, 0.05],
                    "material": {"roughness": 0.2, "metalness": 0.8},
                },
                {
                    "name": "руна_2",
                    "geometry": "BoxGeometry",
                    "color": "#ffdd00",
                    "position": [-0.5, 0.9, 0.5],
                    "scale": [0.1, 0.05, 0.05],
                    "material": {"roughness": 0.2, "metalness": 0.8},
                },
                {
                    "name": "руна_3",
                    "geometry": "BoxGeometry",
                    "color": "#ffdd00",
                    "position": [0.5, 0.9, -0.5],
                    "scale": [0.1, 0.05, 0.05],
                    "material": {"roughness": 0.2, "metalness": 0.8},
                },
                {
                    "name": "руна_4",
                    "geometry": "BoxGeometry",
                    "color": "#ffdd00",
                    "position": [-0.5, 0.9, -0.5],
                    "scale": [0.1, 0.05, 0.05],
                    "material": {"roughness": 0.2, "metalness": 0.8},
                },
            ]
        },
        "animation": {
            "type": "flicker",
            "target": "child:свечение",
            "params": {"min_intensity": 0.3, "max_intensity": 1.0, "speed": 2.5},
        },
    },
    # ================================================================
    # 3. ГОТИЧЕСКИЙ ФОНАРЬ
    # ================================================================
    {
        "name": "🏮 Готический фонарь",
        "description": "Уличный фонарь в викторианском стиле",
        "tags": ["фонарь", "готика", "улица", "освещение"],
        "data": {
            "children": [
                {
                    "name": "основание",
                    "geometry": "CylinderGeometry",
                    "color": "#2c2c2c",
                    "position": [0, 0.15, 0],
                    "scale": [0.5, 0.3, 0.5],
                    "material": {"roughness": 0.4, "metalness": 0.7},
                },
                {
                    "name": "столб",
                    "geometry": "CylinderGeometry",
                    "color": "#3a3a3a",
                    "position": [0, 1.5, 0],
                    "scale": [0.12, 2.5, 0.12],
                    "material": {"roughness": 0.5, "metalness": 0.6},
                },
                {
                    "name": "корпус",
                    "geometry": "CylinderGeometry",
                    "color": "#1a1a1a",
                    "position": [0, 3.2, 0],
                    "scale": [0.35, 0.6, 0.35],
                    "material": {"roughness": 0.3, "metalness": 0.8},
                },
                {
                    "name": "стекло",
                    "geometry": "CylinderGeometry",
                    "color": "#ffffcc",
                    "position": [0, 3.2, 0],
                    "scale": [0.28, 0.5, 0.28],
                    "material": {
                        "roughness": 0.1,
                        "metalness": 0.1,
                        "opacity": 0.5,
                        "transparent": True,
                    },
                },
                {
                    "name": "крышка",
                    "geometry": "ConeGeometry",
                    "color": "#2c2c2c",
                    "position": [0, 3.55, 0],
                    "scale": [0.35, 0.3, 0.35],
                    "material": {"roughness": 0.3, "metalness": 0.8},
                },
                {
                    "name": "шпиль",
                    "geometry": "CylinderGeometry",
                    "color": "#ffd700",
                    "position": [0, 3.85, 0],
                    "scale": [0.04, 0.3, 0.04],
                    "material": {"roughness": 0.1, "metalness": 0.9},
                },
                {
                    "name": "лампа",
                    "geometry": "SphereGeometry",
                    "color": "#ffffff",
                    "position": [0, 3.2, 0],
                    "scale": [0.12, 0.12, 0.12],
                    "material": {"roughness": 0.0, "metalness": 0.0},
                },
            ]
        },
        "animation": {
            "type": "flicker",
            "target": "child:лампа",
            "params": {"min_intensity": 0.6, "max_intensity": 1.0, "speed": 4.0},
        },
    },
    # ================================================================
    # 4. КОСТЁР (огонь + дрова + камни)
    # ================================================================
    {
        "name": "🔥 Костёр",
        "description": "Походный костёр с дровами и камнями",
        "tags": ["огонь", "лагерь", "природа", "свет"],
        "data": {
            "children": [
                # Камни по кругу
                {
                    "name": "камень_1",
                    "geometry": "IcosahedronGeometry",
                    "color": "#7a7a7a",
                    "position": [0.5, 0.05, 0],
                    "scale": [0.15, 0.1, 0.15],
                    "material": {"roughness": 0.9},
                },
                {
                    "name": "камень_2",
                    "geometry": "IcosahedronGeometry",
                    "color": "#6e6e6e",
                    "position": [0.25, 0.04, 0.45],
                    "scale": [0.13, 0.09, 0.13],
                    "material": {"roughness": 0.9},
                },
                {
                    "name": "камень_3",
                    "geometry": "IcosahedronGeometry",
                    "color": "#808080",
                    "position": [-0.3, 0.03, 0.4],
                    "scale": [0.14, 0.08, 0.14],
                    "material": {"roughness": 0.9},
                },
                {
                    "name": "камень_4",
                    "geometry": "IcosahedronGeometry",
                    "color": "#757575",
                    "position": [-0.5, 0.05, 0],
                    "scale": [0.15, 0.1, 0.15],
                    "material": {"roughness": 0.9},
                },
                {
                    "name": "камень_5",
                    "geometry": "IcosahedronGeometry",
                    "color": "#6e6e6e",
                    "position": [-0.2, 0.04, -0.45],
                    "scale": [0.13, 0.09, 0.13],
                    "material": {"roughness": 0.9},
                },
                {
                    "name": "камень_6",
                    "geometry": "IcosahedronGeometry",
                    "color": "#7a7a7a",
                    "position": [0.35, 0.03, -0.4],
                    "scale": [0.14, 0.08, 0.14],
                    "material": {"roughness": 0.9},
                },
                # Дрова
                {
                    "name": "дрова_1",
                    "geometry": "CylinderGeometry",
                    "color": "#5d4037",
                    "position": [0, 0.07, 0.15],
                    "rotation": [1.57, 0, 0],
                    "scale": [0.08, 0.6, 0.08],
                    "material": {"roughness": 0.95},
                },
                {
                    "name": "дрова_2",
                    "geometry": "CylinderGeometry",
                    "color": "#4e342e",
                    "position": [0.15, 0.07, -0.1],
                    "rotation": [1.57, 0.5, 0],
                    "scale": [0.07, 0.55, 0.07],
                    "material": {"roughness": 0.95},
                },
                {
                    "name": "дрова_3",
                    "geometry": "CylinderGeometry",
                    "color": "#5d4037",
                    "position": [-0.1, 0.08, -0.05],
                    "rotation": [1.57, -0.3, 0],
                    "scale": [0.08, 0.5, 0.08],
                    "material": {"roughness": 0.95},
                },
                # Огонь (конусы)
                {
                    "name": "огонь_1",
                    "geometry": "ConeGeometry",
                    "color": "#ff6600",
                    "position": [0, 0.25, 0],
                    "scale": [0.3, 0.5, 0.3],
                    "material": {"roughness": 0.1, "metalness": 0.0},
                },
                {
                    "name": "огонь_2",
                    "geometry": "ConeGeometry",
                    "color": "#ffaa00",
                    "position": [0.05, 0.35, 0.05],
                    "scale": [0.2, 0.35, 0.2],
                    "material": {"roughness": 0.1},
                },
                {
                    "name": "огонь_3",
                    "geometry": "ConeGeometry",
                    "color": "#ffdd00",
                    "position": [-0.03, 0.42, -0.02],
                    "scale": [0.12, 0.25, 0.12],
                    "material": {"roughness": 0.05},
                },
            ]
        },
        "animation": {
            "type": "flicker",
            "target": "child:огонь_1",
            "params": {"min_intensity": 0.7, "max_intensity": 1.0, "speed": 8.0},
        },
    },
    # ================================================================
    # 5. ТРОН ИЗ КОСТЕЙ (для тёмного властелина)
    # ================================================================
    {
        "name": "💀 Трон из костей",
        "description": "Зловещий трон, собранный из гигантских костей",
        "tags": ["трон", "тёмный", "готика", "эпический"],
        "data": {
            "children": [
                # Сиденье
                {
                    "name": "сиденье",
                    "geometry": "BoxGeometry",
                    "color": "#d4c5a9",
                    "position": [0, 0.4, 0],
                    "scale": [1.5, 0.3, 1.2],
                    "material": {"roughness": 0.7, "metalness": 0.1},
                },
                # Рёбра спинки
                {
                    "name": "ребро_л",
                    "geometry": "CylinderGeometry",
                    "color": "#c4b5a0",
                    "position": [-0.6, 1.2, -0.3],
                    "rotation": [0.2, 0, 0.1],
                    "scale": [0.08, 1.5, 0.08],
                    "material": {"roughness": 0.7},
                },
                {
                    "name": "ребро_ц",
                    "geometry": "CylinderGeometry",
                    "color": "#d4c5a9",
                    "position": [0, 1.4, -0.4],
                    "rotation": [0.1, 0, 0],
                    "scale": [0.09, 1.7, 0.09],
                    "material": {"roughness": 0.7},
                },
                {
                    "name": "ребро_п",
                    "geometry": "CylinderGeometry",
                    "color": "#c4b5a0",
                    "position": [0.6, 1.2, -0.3],
                    "rotation": [0.2, 0, -0.1],
                    "scale": [0.08, 1.5, 0.08],
                    "material": {"roughness": 0.7},
                },
                # Черепа на подлокотниках
                {
                    "name": "череп_л",
                    "geometry": "SphereGeometry",
                    "color": "#e8dcc8",
                    "position": [-0.8, 0.9, 0.3],
                    "scale": [0.22, 0.2, 0.25],
                    "material": {"roughness": 0.5},
                },
                {
                    "name": "череп_п",
                    "geometry": "SphereGeometry",
                    "color": "#e8dcc8",
                    "position": [0.8, 0.9, 0.3],
                    "scale": [0.22, 0.2, 0.25],
                    "material": {"roughness": 0.5},
                },
                # Глаза черепов (рубины)
                {
                    "name": "глаз_л",
                    "geometry": "SphereGeometry",
                    "color": "#ff0044",
                    "position": [-0.78, 0.93, 0.5],
                    "scale": [0.05, 0.05, 0.05],
                    "material": {"roughness": 0.05, "metalness": 0.9},
                },
                {
                    "name": "глаз_п",
                    "geometry": "SphereGeometry",
                    "color": "#ff0044",
                    "position": [0.82, 0.93, 0.5],
                    "scale": [0.05, 0.05, 0.05],
                    "material": {"roughness": 0.05, "metalness": 0.9},
                },
                # Подлокотники
                {
                    "name": "подлокотник_л",
                    "geometry": "BoxGeometry",
                    "color": "#b8a890",
                    "position": [-0.7, 0.7, 0.2],
                    "scale": [0.2, 0.2, 0.4],
                    "material": {"roughness": 0.8},
                },
                {
                    "name": "подлокотник_п",
                    "geometry": "BoxGeometry",
                    "color": "#b8a890",
                    "position": [0.7, 0.7, 0.2],
                    "scale": [0.2, 0.2, 0.4],
                    "material": {"roughness": 0.8},
                },
            ]
        },
    },
    # ================================================================
    # 6. ПАРЯЩИЙ ОСТРОВ (фэнтези)
    # ================================================================
    {
        "name": "🏝️ Парящий остров",
        "description": "Маленький летающий остров с водопадом и деревом",
        "tags": ["остров", "фэнтези", "магия", "небо"],
        "data": {
            "children": [
                # Земля
                {
                    "name": "земля_верх",
                    "geometry": "SphereGeometry",
                    "color": "#5d8a3c",
                    "position": [0, 0, 0],
                    "scale": [1.2, 0.3, 1.0],
                    "material": {"roughness": 0.9},
                },
                {
                    "name": "земля_низ",
                    "geometry": "ConeGeometry",
                    "color": "#4a3020",
                    "position": [0, -0.7, 0],
                    "scale": [1.1, 0.8, 1.0],
                    "material": {"roughness": 0.9},
                },
                # Камни снизу
                {
                    "name": "камень_низ_1",
                    "geometry": "IcosahedronGeometry",
                    "color": "#6a5a4a",
                    "position": [0.3, -1.1, 0.2],
                    "scale": [0.2, 0.15, 0.2],
                    "material": {"roughness": 0.85},
                },
                {
                    "name": "камень_низ_2",
                    "geometry": "IcosahedronGeometry",
                    "color": "#5a4a3a",
                    "position": [-0.4, -1.0, -0.2],
                    "scale": [0.18, 0.12, 0.18],
                    "material": {"roughness": 0.85},
                },
                # Дерево
                {
                    "name": "ствол",
                    "geometry": "CylinderGeometry",
                    "color": "#6b4c3b",
                    "position": [0.2, 0.6, 0.1],
                    "scale": [0.1, 1.0, 0.1],
                    "material": {"roughness": 0.9},
                },
                {
                    "name": "крона",
                    "geometry": "SphereGeometry",
                    "color": "#3a6b2a",
                    "position": [0.2, 1.2, 0.1],
                    "scale": [0.5, 0.4, 0.5],
                    "material": {"roughness": 0.8},
                },
                # Маленький водопад (синие полупрозрачные цилиндры)
                {
                    "name": "вода_1",
                    "geometry": "CylinderGeometry",
                    "color": "#4488cc",
                    "position": [-0.5, -0.5, 0.4],
                    "rotation": [0.2, 0, 0],
                    "scale": [0.04, 0.6, 0.04],
                    "material": {
                        "roughness": 0.1,
                        "metalness": 0.0,
                        "opacity": 0.5,
                        "transparent": True,
                    },
                },
                {
                    "name": "вода_2",
                    "geometry": "CylinderGeometry",
                    "color": "#5599dd",
                    "position": [-0.45, -0.7, 0.45],
                    "rotation": [0.3, 0, 0],
                    "scale": [0.03, 0.5, 0.03],
                    "material": {"roughness": 0.1, "opacity": 0.4, "transparent": True},
                },
            ]
        },
        "animation": {
            "type": "sway",
            "target": "self",
            "params": {"amplitude": 0.3, "speed": 0.5},
        },
    },
    # ================================================================
    # 7. КОЛОДЕЦ (уже есть в tools, но как самостоятельный ассет)
    # ================================================================
    {
        "name": "🪣 Деревенский колодец",
        "description": "Каменный колодец с деревянной крышей и ведром",
        "tags": ["колодец", "деревня", "вода", "строение"],
        "data": {
            "children": [
                {
                    "name": "основание",
                    "geometry": "CylinderGeometry",
                    "color": "#8B7355",
                    "position": [0, 0.2, 0],
                    "scale": [1.3, 0.4, 1.3],
                    "material": {"roughness": 0.9},
                },
                {
                    "name": "стенка",
                    "geometry": "TorusGeometry",
                    "color": "#A0896E",
                    "position": [0, 0.9, 0],
                    "scale": [1.1, 0.25, 1.1],
                    "material": {"roughness": 0.85},
                },
                {
                    "name": "верхнее_кольцо",
                    "geometry": "TorusGeometry",
                    "color": "#9B8B7A",
                    "position": [0, 1.5, 0],
                    "scale": [1.1, 0.2, 1.1],
                    "material": {"roughness": 0.8},
                },
                {
                    "name": "стойка_л",
                    "geometry": "BoxGeometry",
                    "color": "#6B4226",
                    "position": [-0.85, 2.0, 0],
                    "scale": [0.2, 2.0, 0.2],
                    "material": {"roughness": 0.9},
                },
                {
                    "name": "стойка_п",
                    "geometry": "BoxGeometry",
                    "color": "#6B4226",
                    "position": [0.85, 2.0, 0],
                    "scale": [0.2, 2.0, 0.2],
                    "material": {"roughness": 0.9},
                },
                {
                    "name": "перекладина",
                    "geometry": "CylinderGeometry",
                    "color": "#5D4037",
                    "position": [0, 3.1, 0],
                    "rotation": [0, 0, 1.57],
                    "scale": [0.1, 1.9, 0.1],
                    "material": {"roughness": 0.85},
                },
                {
                    "name": "крыша_л",
                    "geometry": "BoxGeometry",
                    "color": "#A0522D",
                    "position": [-0.45, 3.2, 0],
                    "rotation": [0, 0, 0.4],
                    "scale": [0.9, 0.1, 1.2],
                    "material": {"roughness": 0.8},
                },
                {
                    "name": "крыша_п",
                    "geometry": "BoxGeometry",
                    "color": "#A0522D",
                    "position": [0.45, 3.2, 0],
                    "rotation": [0, 0, -0.4],
                    "scale": [0.9, 0.1, 1.2],
                    "material": {"roughness": 0.8},
                },
            ]
        },
    },
    # ================================================================
    # 8. АРКА ПОБЕДЫ
    # ================================================================
    {
        "name": "🏛️ Триумфальная арка",
        "description": "Величественная арка с колоннами и золотыми украшениями",
        "tags": ["арка", "архитектура", "город", "эпический"],
        "data": {
            "children": [
                {
                    "name": "колонна_л",
                    "geometry": "BoxGeometry",
                    "color": "#D2B48C",
                    "position": [-1.5, 1.5, 0],
                    "scale": [0.5, 3.0, 0.5],
                    "material": {"roughness": 0.6},
                },
                {
                    "name": "колонна_п",
                    "geometry": "BoxGeometry",
                    "color": "#D2B48C",
                    "position": [1.5, 1.5, 0],
                    "scale": [0.5, 3.0, 0.5],
                    "material": {"roughness": 0.6},
                },
                {
                    "name": "архитрав",
                    "geometry": "BoxGeometry",
                    "color": "#FFD700",
                    "position": [0, 3.2, 0],
                    "scale": [3.8, 0.4, 0.6],
                    "material": {"roughness": 0.2, "metalness": 0.8},
                },
                {
                    "name": "фронтон",
                    "geometry": "BoxGeometry",
                    "color": "#FFD700",
                    "position": [0, 3.7, 0],
                    "scale": [2.2, 0.7, 0.6],
                    "material": {"roughness": 0.2, "metalness": 0.8},
                },
                {
                    "name": "шар",
                    "geometry": "SphereGeometry",
                    "color": "#FFD700",
                    "position": [0, 4.3, 0],
                    "scale": [0.25, 0.25, 0.25],
                    "material": {"roughness": 0.1, "metalness": 0.9},
                },
                {
                    "name": "база_л",
                    "geometry": "BoxGeometry",
                    "color": "#B8A080",
                    "position": [-1.5, 0.15, 0],
                    "scale": [0.7, 0.3, 0.7],
                    "material": {"roughness": 0.7},
                },
                {
                    "name": "база_п",
                    "geometry": "BoxGeometry",
                    "color": "#B8A080",
                    "position": [1.5, 0.15, 0],
                    "scale": [0.7, 0.3, 0.7],
                    "material": {"roughness": 0.7},
                },
            ]
        },
    },
    # ================================================================
    # 9. ГРИБНОЙ ДОМИК (фэнтези)
    # ================================================================
    {
        "name": "🍄 Грибной домик",
        "description": "Сказочный домик в виде гриба с дверью и окном",
        "tags": ["дом", "гриб", "фэнтези", "сказка"],
        "data": {
            "children": [
                {
                    "name": "ножка",
                    "geometry": "CylinderGeometry",
                    "color": "#F5DEB3",
                    "position": [0, 0.8, 0],
                    "scale": [0.5, 1.6, 0.5],
                    "material": {"roughness": 0.8},
                },
                {
                    "name": "шляпка",
                    "geometry": "SphereGeometry",
                    "color": "#CC3333",
                    "position": [0, 1.6, 0],
                    "scale": [1.1, 0.5, 1.1],
                    "material": {"roughness": 0.6},
                },
                {
                    "name": "дверь",
                    "geometry": "BoxGeometry",
                    "color": "#6B4226",
                    "position": [0, 0.5, 0.45],
                    "scale": [0.2, 0.5, 0.05],
                    "material": {"roughness": 0.8},
                },
                {
                    "name": "окно",
                    "geometry": "BoxGeometry",
                    "color": "#ffff88",
                    "position": [0.3, 1.0, 0.4],
                    "scale": [0.12, 0.15, 0.03],
                    "material": {"roughness": 0.1, "metalness": 0.0},
                },
                {
                    "name": "точка_1",
                    "geometry": "SphereGeometry",
                    "color": "#ffffff",
                    "position": [0.3, 1.8, 0.4],
                    "scale": [0.08, 0.08, 0.08],
                    "material": {"roughness": 0.3},
                },
                {
                    "name": "точка_2",
                    "geometry": "SphereGeometry",
                    "color": "#ffffff",
                    "position": [-0.4, 1.9, -0.2],
                    "scale": [0.06, 0.06, 0.06],
                    "material": {"roughness": 0.3},
                },
                {
                    "name": "точка_3",
                    "geometry": "SphereGeometry",
                    "color": "#ffffff",
                    "position": [0.2, 1.75, -0.5],
                    "scale": [0.07, 0.07, 0.07],
                    "material": {"roughness": 0.3},
                },
            ]
        },
    },
    # ================================================================
    # 10. КОРАБЛЬ-ПРИЗРАК
    # ================================================================
    {
        "name": "👻 Корабль-призрак",
        "description": "Прозрачный летучий корабль с призрачными парусами",
        "tags": ["корабль", "призрак", "небо", "эпический"],
        "data": {
            "children": [
                {
                    "name": "корпус",
                    "geometry": "BoxGeometry",
                    "color": "#8899aa",
                    "position": [0, 0, 0],
                    "scale": [2.5, 0.3, 0.6],
                    "material": {
                        "roughness": 0.3,
                        "metalness": 0.5,
                        "opacity": 0.6,
                        "transparent": True,
                    },
                },
                {
                    "name": "нос",
                    "geometry": "ConeGeometry",
                    "color": "#8899aa",
                    "position": [1.5, 0, 0],
                    "rotation": [0, 0, 1.57],
                    "scale": [0.3, 0.4, 0.4],
                    "material": {
                        "roughness": 0.3,
                        "metalness": 0.5,
                        "opacity": 0.6,
                        "transparent": True,
                    },
                },
                {
                    "name": "мачта_1",
                    "geometry": "CylinderGeometry",
                    "color": "#aabbcc",
                    "position": [-0.5, 0.8, 0],
                    "scale": [0.05, 1.5, 0.05],
                    "material": {
                        "roughness": 0.3,
                        "metalness": 0.5,
                        "opacity": 0.5,
                        "transparent": True,
                    },
                },
                {
                    "name": "мачта_2",
                    "geometry": "CylinderGeometry",
                    "color": "#aabbcc",
                    "position": [0.5, 0.8, 0],
                    "scale": [0.05, 1.5, 0.05],
                    "material": {
                        "roughness": 0.3,
                        "metalness": 0.5,
                        "opacity": 0.5,
                        "transparent": True,
                    },
                },
                {
                    "name": "парус_л",
                    "geometry": "PlaneGeometry",
                    "color": "#ccccdd",
                    "position": [-0.5, 1.0, 0.3],
                    "rotation": [0, 0.2, 0],
                    "scale": [0.8, 0.6, 0.01],
                    "material": {"roughness": 0.2, "opacity": 0.3, "transparent": True},
                },
                {
                    "name": "парус_п",
                    "geometry": "PlaneGeometry",
                    "color": "#ccccdd",
                    "position": [0.5, 1.0, 0.3],
                    "rotation": [0, -0.2, 0],
                    "scale": [0.8, 0.6, 0.01],
                    "material": {"roughness": 0.2, "opacity": 0.3, "transparent": True},
                },
            ]
        },
        "animation": {
            "type": "sway",
            "target": "self",
            "params": {"amplitude": 0.5, "speed": 0.2},
        },
    },
    # ================================================================
    # 11. ЯПОНСКИЕ ВРАТА ТОРИИ
    # ================================================================
    {
        "name": "⛩️ Врата Тории",
        "description": "Традиционные японские ритуальные врата",
        "tags": ["япония", "врата", "храм", "восток"],
        "data": {
            "children": [
                {
                    "name": "столб_л",
                    "geometry": "CylinderGeometry",
                    "color": "#cc4444",
                    "position": [-1.5, 1.5, 0],
                    "scale": [0.2, 3.0, 0.2],
                    "material": {"roughness": 0.5, "metalness": 0.1},
                },
                {
                    "name": "столб_п",
                    "geometry": "CylinderGeometry",
                    "color": "#cc4444",
                    "position": [1.5, 1.5, 0],
                    "scale": [0.2, 3.0, 0.2],
                    "material": {"roughness": 0.5, "metalness": 0.1},
                },
                {
                    "name": "верхняя_балка",
                    "geometry": "BoxGeometry",
                    "color": "#cc4444",
                    "position": [0, 3.2, 0],
                    "scale": [3.8, 0.2, 0.4],
                    "material": {"roughness": 0.5, "metalness": 0.1},
                },
                {
                    "name": "изогнутая_балка",
                    "geometry": "BoxGeometry",
                    "color": "#aa3333",
                    "position": [0, 3.5, 0],
                    "rotation": [0, 0, 0.02],
                    "scale": [3.6, 0.15, 0.35],
                    "material": {"roughness": 0.5, "metalness": 0.2},
                },
            ]
        },
    },
    # ================================================================
    # 12. ТЫКВА НА ХЭЛЛОУИН
    # ================================================================
    {
        "name": "🎃 Тыква Хэллоуина",
        "description": "Светящаяся тыква с вырезанным лицом",
        "tags": ["хэллоуин", "тыква", "праздник", "свет"],
        "data": {
            "children": [
                {
                    "name": "тыква",
                    "geometry": "SphereGeometry",
                    "color": "#ff6600",
                    "position": [0, 0.3, 0],
                    "scale": [0.8, 0.5, 0.7],
                    "material": {"roughness": 0.6},
                },
                {
                    "name": "хвостик",
                    "geometry": "CylinderGeometry",
                    "color": "#4a5a2a",
                    "position": [0, 0.6, 0],
                    "scale": [0.06, 0.2, 0.06],
                    "material": {"roughness": 0.9},
                },
                {
                    "name": "глаз_л",
                    "geometry": "BoxGeometry",
                    "color": "#ffff00",
                    "position": [-0.2, 0.4, 0.6],
                    "scale": [0.1, 0.12, 0.03],
                    "material": {"roughness": 0.1, "metalness": 0.0},
                },
                {
                    "name": "глаз_п",
                    "geometry": "BoxGeometry",
                    "color": "#ffff00",
                    "position": [0.2, 0.4, 0.6],
                    "scale": [0.1, 0.12, 0.03],
                    "material": {"roughness": 0.1},
                },
                {
                    "name": "рот",
                    "geometry": "BoxGeometry",
                    "color": "#ffff00",
                    "position": [0, 0.2, 0.6],
                    "scale": [0.25, 0.08, 0.03],
                    "material": {"roughness": 0.1},
                },
                {
                    "name": "свечение",
                    "geometry": "SphereGeometry",
                    "color": "#ffaa00",
                    "position": [0, 0.25, 0],
                    "scale": [0.45, 0.3, 0.35],
                    "material": {"roughness": 0.0, "opacity": 0.4, "transparent": True},
                },
            ]
        },
        "animation": {
            "type": "flicker",
            "target": "child:свечение",
            "params": {"min_intensity": 0.5, "max_intensity": 1.0, "speed": 6.0},
        },
    },
    # ================================================================
    # 13. КОСМИЧЕСКИЙ АЛТАРЬ
    # ================================================================
    {
        "name": "🌌 Космический алтарь",
        "description": "Футуристический алтарь с голографическими элементами",
        "tags": ["космос", "алтарь", "футуризм", "магия"],
        "data": {
            "children": [
                {
                    "name": "база",
                    "geometry": "CylinderGeometry",
                    "color": "#1a1a3a",
                    "position": [0, 0.1, 0],
                    "scale": [1.5, 0.2, 1.5],
                    "material": {"roughness": 0.3, "metalness": 0.9},
                },
                {
                    "name": "кольцо_1",
                    "geometry": "TorusGeometry",
                    "color": "#334466",
                    "position": [0, 0.5, 0],
                    "scale": [0.8, 0.05, 0.8],
                    "material": {"roughness": 0.1, "metalness": 0.9},
                },
                {
                    "name": "кольцо_2",
                    "geometry": "TorusGeometry",
                    "color": "#445577",
                    "position": [0, 0.8, 0],
                    "rotation": [1.57, 0, 0],
                    "scale": [0.6, 0.04, 0.6],
                    "material": {"roughness": 0.1, "metalness": 0.9},
                },
                {
                    "name": "ядро",
                    "geometry": "IcosahedronGeometry",
                    "color": "#6644ff",
                    "position": [0, 1.2, 0],
                    "scale": [0.3, 0.3, 0.3],
                    "material": {"roughness": 0.02, "metalness": 0.95},
                },
                {
                    "name": "свечение",
                    "geometry": "SphereGeometry",
                    "color": "#9966ff",
                    "position": [0, 1.2, 0],
                    "scale": [0.6, 0.6, 0.6],
                    "material": {"roughness": 0.0, "opacity": 0.2, "transparent": True},
                },
            ]
        },
        "animation": {
            "type": "rotate",
            "target": "child:кольцо_1",
            "params": {"axis": "y", "speed": 1.0},
        },
    },
    # ================================================================
    # 14. ДОМИК НА ДЕРЕВЕ
    # ================================================================
    {
        "name": "🏠 Домик на дереве",
        "description": "Уютный домик среди ветвей с лестницей",
        "tags": ["дом", "дерево", "уют", "природа"],
        "data": {
            "children": [
                {
                    "name": "ствол",
                    "geometry": "CylinderGeometry",
                    "color": "#5D4037",
                    "position": [0, 1.0, 0],
                    "scale": [0.3, 2.0, 0.3],
                    "material": {"roughness": 0.9},
                },
                {
                    "name": "пол",
                    "geometry": "BoxGeometry",
                    "color": "#8B7355",
                    "position": [0, 2.2, 0],
                    "scale": [1.8, 0.1, 1.5],
                    "material": {"roughness": 0.8},
                },
                {
                    "name": "стена_фронт",
                    "geometry": "BoxGeometry",
                    "color": "#A0896E",
                    "position": [0, 2.7, 0.7],
                    "scale": [1.8, 0.8, 0.05],
                    "material": {"roughness": 0.8},
                },
                {
                    "name": "стена_бок_л",
                    "geometry": "BoxGeometry",
                    "color": "#9B8B7A",
                    "position": [-0.9, 2.7, 0],
                    "scale": [0.05, 0.8, 1.4],
                    "material": {"roughness": 0.8},
                },
                {
                    "name": "стена_бок_п",
                    "geometry": "BoxGeometry",
                    "color": "#9B8B7A",
                    "position": [0.9, 2.7, 0],
                    "scale": [0.05, 0.8, 1.4],
                    "material": {"roughness": 0.8},
                },
                {
                    "name": "крыша_л",
                    "geometry": "BoxGeometry",
                    "color": "#A0522D",
                    "position": [-0.5, 3.25, 0],
                    "rotation": [0, 0, 0.5],
                    "scale": [1.0, 0.08, 1.6],
                    "material": {"roughness": 0.7},
                },
                {
                    "name": "крыша_п",
                    "geometry": "BoxGeometry",
                    "color": "#A0522D",
                    "position": [0.5, 3.25, 0],
                    "rotation": [0, 0, -0.5],
                    "scale": [1.0, 0.08, 1.6],
                    "material": {"roughness": 0.7},
                },
                {
                    "name": "дверь",
                    "geometry": "BoxGeometry",
                    "color": "#6B4226",
                    "position": [0, 2.3, 0.72],
                    "scale": [0.3, 0.4, 0.03],
                    "material": {"roughness": 0.8},
                },
                {
                    "name": "окно",
                    "geometry": "BoxGeometry",
                    "color": "#aaddff",
                    "position": [0.5, 2.7, 0.7],
                    "scale": [0.2, 0.2, 0.02],
                    "material": {
                        "roughness": 0.1,
                        "metalness": 0.2,
                        "opacity": 0.6,
                        "transparent": True,
                    },
                },
                {
                    "name": "лестница_1",
                    "geometry": "BoxGeometry",
                    "color": "#6B4226",
                    "position": [0.4, 1.5, 0.4],
                    "scale": [0.05, 0.03, 0.2],
                    "material": {"roughness": 0.9},
                },
                {
                    "name": "лестница_2",
                    "geometry": "BoxGeometry",
                    "color": "#6B4226",
                    "position": [0.35, 1.7, 0.3],
                    "scale": [0.05, 0.03, 0.2],
                    "material": {"roughness": 0.9},
                },
            ]
        },
    },
    # ================================================================
    # 15. ФОНТАН С АНГЕЛОМ
    # ================================================================
    {
        "name": "👼 Фонтан с ангелом",
        "description": "Мраморный фонтан со статуей ангела и текущей водой",
        "tags": ["фонтан", "ангел", "город", "вода", "классика"],
        "data": {
            "children": [
                {
                    "name": "бассейн",
                    "geometry": "CylinderGeometry",
                    "color": "#d4d4d4",
                    "position": [0, 0.15, 0],
                    "scale": [1.5, 0.3, 1.5],
                    "material": {"roughness": 0.3, "metalness": 0.2},
                },
                {
                    "name": "пьедестал",
                    "geometry": "CylinderGeometry",
                    "color": "#e0e0e0",
                    "position": [0, 0.6, 0],
                    "scale": [0.5, 0.8, 0.5],
                    "material": {"roughness": 0.3, "metalness": 0.2},
                },
                {
                    "name": "статуя_тело",
                    "geometry": "CylinderGeometry",
                    "color": "#e8e8e8",
                    "position": [0, 1.4, 0],
                    "scale": [0.15, 0.7, 0.15],
                    "material": {"roughness": 0.2, "metalness": 0.3},
                },
                {
                    "name": "статуя_голова",
                    "geometry": "SphereGeometry",
                    "color": "#e8e8e8",
                    "position": [0, 1.85, 0],
                    "scale": [0.13, 0.15, 0.13],
                    "material": {"roughness": 0.2, "metalness": 0.3},
                },
                {
                    "name": "крыло_л",
                    "geometry": "BoxGeometry",
                    "color": "#e8e8e8",
                    "position": [-0.2, 1.6, -0.05],
                    "rotation": [0, 0, 0.5],
                    "scale": [0.3, 0.05, 0.1],
                    "material": {"roughness": 0.2, "metalness": 0.3},
                },
                {
                    "name": "крыло_п",
                    "geometry": "BoxGeometry",
                    "color": "#e8e8e8",
                    "position": [0.2, 1.6, -0.05],
                    "rotation": [0, 0, -0.5],
                    "scale": [0.3, 0.05, 0.1],
                    "material": {"roughness": 0.2, "metalness": 0.3},
                },
                {
                    "name": "вода_верх",
                    "geometry": "CylinderGeometry",
                    "color": "#6699cc",
                    "position": [0, 1.1, 0.3],
                    "scale": [0.04, 0.4, 0.04],
                    "material": {
                        "roughness": 0.05,
                        "opacity": 0.5,
                        "transparent": True,
                    },
                },
            ]
        },
    },
]


class Command(BaseCommand):
    help = "Создаёт крутые готовые ассеты для вдохновения и тестирования"

    def handle(self, *args, **options):
        # Берём первого пользователя как создателя
        owner = User.objects.filter(is_superuser=True).first() or User.objects.first()

        if not owner:
            self.stdout.write(
                self.style.ERROR("❌ Нет пользователей! Создайте суперпользователя.")
            )
            return

        created = 0
        updated = 0

        for asset_data in AWESOME_ASSETS:
            name = asset_data["name"]
            obj, was_created = Asset.objects.update_or_create(
                name=name,
                defaults={
                    "description": asset_data.get("description", ""),
                    "data": asset_data.get("data", {}),
                    "animation": asset_data.get("animation", {}),
                    "tags": asset_data.get("tags", []),
                    "created_by": owner,
                },
            )

            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f"  ✅ {name}"))
            else:
                updated += 1
                self.stdout.write(self.style.WARNING(f"  🔄 {name} (обновлён)"))

        self.stdout.write(
            self.style.SUCCESS(f"\n🎉 Готово! Создано: {created}, обновлено: {updated}")
        )
