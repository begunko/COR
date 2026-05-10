# tools/management/commands/load_all_tools.py
# ==============================================================================
# ПЕРВОНАЧАЛЬНЫЙ ПОСЕВ ИНСТРУМЕНТОВ И НАБОРОВ
#
# Создаёт стартовые наборы с инструментами.
# Вызов: python manage.py load_all_tools
#
# СТРУКТУРА:
#   Набор 1: Базовые фигуры (куб, сфера, цилиндр, конус, пирамида, тор, плоскость)
#   Набор 2: Платоновы тела (тетраэдр, октаэдр, икосаэдр, додекаэдр)
#   Набор 3: Экзотика (торический узел, капсула, кольцо, диск, каркасный куб)
#   Набор 4: Фигуры вращения (ваза, яйцо)
#   Набор 5: Строительные блоки (плита, колонна, арка, ступенька)
#   Набор 6: Органика и формы (сердце, звезда, дерево, кристалл)
#   Набор 7: Сложные конструкции (колодец, фонтан, алтарь, врата)
#   Набор 8: Освещение (точка, прожектор, факел)
# ==============================================================================

from django.core.management.base import BaseCommand
from tools.models import Tool, Toolkit
from users.models import User

# ==============================================================================
# ВСЕ ИНСТРУМЕНТЫ (ГЛОБАЛЬНЫЙ РЕЕСТР)
# ==============================================================================

ALL_TOOLS = [
    # =====================================================================
    # ПРОСТЫЕ ФИГУРЫ
    # =====================================================================
    {
        "name": "cube",
        "display_name": "Куб",
        "tool_type": "create_mesh",
        "default_params": {
            "geometry": "BoxGeometry",
            "width": 1,
            "height": 1,
            "depth": 1,
            "color": "#ff6600",
            "defaultY": 0.5,
        },
        "order": 1,
    },
    {
        "name": "sphere",
        "display_name": "Сфера",
        "tool_type": "create_mesh",
        "default_params": {
            "geometry": "SphereGeometry",
            "radius": 0.5,
            "widthSegments": 32,
            "heightSegments": 32,
            "color": "#3388ff",
            "defaultY": 0.5,
        },
        "order": 2,
    },
    {
        "name": "cylinder",
        "display_name": "Цилиндр",
        "tool_type": "create_mesh",
        "default_params": {
            "geometry": "CylinderGeometry",
            "radiusTop": 0.5,
            "radiusBottom": 0.5,
            "height": 1.5,
            "segments": 32,
            "color": "#00cc44",
            "defaultY": 0.75,
        },
        "order": 3,
    },
    {
        "name": "cone",
        "display_name": "Конус",
        "tool_type": "create_mesh",
        "default_params": {
            "geometry": "ConeGeometry",
            "radius": 0.5,
            "height": 1.5,
            "segments": 32,
            "color": "#ffcc00",
            "defaultY": 0.75,
        },
        "order": 4,
    },
    {
        "name": "pyramid",
        "display_name": "Пирамида",
        "tool_type": "create_mesh",
        "default_params": {
            "geometry": "ConeGeometry",
            "radius": 0.7,
            "height": 1.5,
            "radialSegments": 4,
            "color": "#cc33ff",
            "defaultY": 0.75,
        },
        "order": 5,
    },
    {
        "name": "torus",
        "display_name": "Тор (бублик)",
        "tool_type": "create_mesh",
        "default_params": {
            "geometry": "TorusGeometry",
            "radius": 0.7,
            "tube": 0.3,
            "radialSegments": 16,
            "tubularSegments": 32,
            "color": "#ff8833",
            "defaultY": 1.0,
        },
        "order": 6,
    },
    {
        "name": "plane",
        "display_name": "Плоскость",
        "tool_type": "create_mesh",
        "default_params": {
            "geometry": "PlaneGeometry",
            "width": 5,
            "height": 5,
            "color": "#888888",
            "defaultY": 0.0,
        },
        "order": 7,
    },
    # =====================================================================
    # ПЛАТОНОВЫ ТЕЛА
    # =====================================================================
    {
        "name": "tetrahedron",
        "display_name": "Тетраэдр",
        "tool_type": "create_mesh",
        "default_params": {
            "geometry": "TetrahedronGeometry",
            "radius": 0.7,
            "color": "#ff4488",
            "defaultY": 0.7,
        },
        "order": 1,
    },
    {
        "name": "octahedron",
        "display_name": "Октаэдр",
        "tool_type": "create_mesh",
        "default_params": {
            "geometry": "OctahedronGeometry",
            "radius": 0.7,
            "color": "#44ff88",
            "defaultY": 0.7,
        },
        "order": 2,
    },
    {
        "name": "icosahedron",
        "display_name": "Икосаэдр",
        "tool_type": "create_mesh",
        "default_params": {
            "geometry": "IcosahedronGeometry",
            "radius": 0.7,
            "color": "#4488ff",
            "defaultY": 0.7,
        },
        "order": 3,
    },
    {
        "name": "dodecahedron",
        "display_name": "Додекаэдр",
        "tool_type": "create_mesh",
        "default_params": {
            "geometry": "DodecahedronGeometry",
            "radius": 0.7,
            "color": "#ff8844",
            "defaultY": 0.7,
        },
        "order": 4,
    },
    # =====================================================================
    # ЭКЗОТИКА
    # =====================================================================
    {
        "name": "torus_knot",
        "display_name": "Торический узел",
        "tool_type": "create_mesh",
        "default_params": {
            "geometry": "TorusKnotGeometry",
            "radius": 0.8,
            "tube": 0.2,
            "tubularSegments": 64,
            "radialSegments": 8,
            "p": 2,
            "q": 3,
            "color": "#44ffcc",
            "defaultY": 1.5,
        },
        "order": 1,
    },
    {
        "name": "capsule",
        "display_name": "Капсула",
        "tool_type": "create_mesh",
        "default_params": {
            "geometry": "CapsuleGeometry",
            "radius": 0.3,
            "length": 1.5,
            "capSegments": 8,
            "radialSegments": 32,
            "color": "#ff44cc",
            "defaultY": 0.75,
        },
        "order": 2,
    },
    {
        "name": "ring",
        "display_name": "Кольцо",
        "tool_type": "create_mesh",
        "default_params": {
            "geometry": "RingGeometry",
            "innerRadius": 0.5,
            "outerRadius": 1.0,
            "thetaSegments": 32,
            "color": "#cccc44",
            "defaultY": 0.5,
        },
        "order": 3,
    },
    {
        "name": "disc",
        "display_name": "Диск",
        "tool_type": "create_mesh",
        "default_params": {
            "geometry": "CircleGeometry",
            "radius": 1.0,
            "segments": 32,
            "color": "#cccccc",
            "defaultY": 0.0,
        },
        "order": 4,
    },
    {
        "name": "wireframe_cube",
        "display_name": "Каркасный куб",
        "tool_type": "create_mesh",
        "default_params": {
            "geometry": "BoxGeometry",
            "width": 1,
            "height": 1,
            "depth": 1,
            "color": "#00ff88",
            "wireframe": True,
            "opacity": 0.8,
            "defaultY": 0.5,
        },
        "order": 5,
    },
    # =====================================================================
    # ФИГУРЫ ВРАЩЕНИЯ
    # =====================================================================
    {
        "name": "vase",
        "display_name": "Ваза",
        "tool_type": "create_mesh",
        "default_params": {
            "geometry": "LatheGeometry",
            "profile": "vase",
            "segments": 32,
            "color": "#ffaa44",
            "defaultY": 0.5,
        },
        "order": 1,
    },
    {
        "name": "egg",
        "display_name": "Яйцо",
        "tool_type": "create_mesh",
        "default_params": {
            "geometry": "LatheGeometry",
            "profile": "egg",
            "segments": 32,
            "color": "#ffffff",
            "defaultY": 0.5,
        },
        "order": 2,
    },
    # =====================================================================
    # СТРОИТЕЛЬНЫЕ БЛОКИ
    # =====================================================================
    {
        "name": "slab",
        "display_name": "Плита",
        "tool_type": "create_mesh",
        "default_params": {
            "geometry": "BoxGeometry",
            "width": 3,
            "height": 0.2,
            "depth": 2,
            "color": "#8B7355",
            "roughness": 0.9,
            "defaultY": 0.1,
        },
        "order": 1,
    },
    {
        "name": "pillar",
        "display_name": "Колонна",
        "tool_type": "create_mesh",
        "default_params": {
            "geometry": "CylinderGeometry",
            "radiusTop": 0.3,
            "radiusBottom": 0.3,
            "height": 3,
            "segments": 16,
            "color": "#D2B48C",
            "roughness": 0.8,
            "defaultY": 1.5,
        },
        "order": 2,
    },
    {
        "name": "arch",
        "display_name": "Арка",
        "tool_type": "create_mesh",
        "default_params": {
            "geometry": "TorusGeometry",
            "radius": 1.2,
            "tube": 0.15,
            "arc": 3.14159,
            "color": "#C8A882",
            "roughness": 0.7,
            "defaultY": 1.2,
        },
        "order": 3,
    },
    {
        "name": "step",
        "display_name": "Ступенька",
        "tool_type": "create_mesh",
        "default_params": {
            "geometry": "BoxGeometry",
            "width": 2,
            "height": 0.3,
            "depth": 0.6,
            "color": "#9E9E9E",
            "roughness": 0.8,
            "defaultY": 0.15,
        },
        "order": 4,
    },
    # =====================================================================
    # ОРГАНИКА И ФОРМЫ
    # =====================================================================
    {
        "name": "heart",
        "display_name": "Сердце ❤️",
        "tool_type": "create_mesh",
        "default_params": {
            "geometry": "ShapeGeometry",
            "shape": "heart",
            "extrudeDepth": 0.2,
            "bevelThickness": 0.05,
            "bevelSize": 0.05,
            "bevelSegments": 3,
            "color": "#ff2244",
            "metalness": 0.3,
            "roughness": 0.2,
            "defaultY": 0.5,
        },
        "order": 1,
    },
    {
        "name": "star",
        "display_name": "Звезда ⭐",
        "tool_type": "create_mesh",
        "default_params": {
            "geometry": "ShapeGeometry",
            "shape": "star",
            "extrudeDepth": 0.2,
            "bevelThickness": 0.03,
            "bevelSize": 0.03,
            "bevelSegments": 2,
            "color": "#ffdd00",
            "metalness": 0.5,
            "roughness": 0.1,
            "defaultY": 0.5,
        },
        "order": 2,
    },
    # =====================================================================
    # ОСВЕЩЕНИЕ
    # =====================================================================
    {
        "name": "point_light",
        "display_name": "Точечный свет",
        "tool_type": "create_light",
        "default_params": {
            "light_type": "point",
            "color": "#ffffff",
            "intensity": 1.0,
            "range": 10,
            "defaultY": 2.0,
        },
        "order": 1,
    },
    {
        "name": "spot_light",
        "display_name": "Прожектор",
        "tool_type": "create_light",
        "default_params": {
            "light_type": "spot",
            "color": "#ffeebb",
            "intensity": 2.0,
            "range": 15,
            "angle": 0.5,
            "penumbra": 0.3,
            "defaultY": 3.0,
        },
        "order": 2,
    },
    {
        "name": "torch_light",
        "display_name": "Факел",
        "tool_type": "create_light",
        "default_params": {
            "light_type": "point",
            "color": "#ff8833",
            "intensity": 0.8,
            "range": 5,
            "defaultY": 1.5,
        },
        "order": 3,
    },
]


# ==============================================================================
# ГРУППОВЫЕ ФИГУРЫ (СРЕДНЯЯ СЛОЖНОСТЬ)
# ==============================================================================

GROUP_TOOLS = [
    {
        "name": "tree_simple",
        "display_name": "Дерево 🌳",
        "tool_type": "create_mesh",
        "default_params": {
            "geometry": "Group",
            "children": [
                {
                    "name": "ствол",
                    "geometry": "CylinderGeometry",
                    "radiusTop": 0.15,
                    "radiusBottom": 0.25,
                    "height": 2.5,
                    "segments": 8,
                    "color": "#5D4037",
                    "roughness": 0.9,
                    "position": [0, 1.25, 0],
                },
                {
                    "name": "крона_низ",
                    "geometry": "SphereGeometry",
                    "radius": 0.8,
                    "widthSegments": 8,
                    "heightSegments": 8,
                    "color": "#2E7D32",
                    "roughness": 0.8,
                    "position": [0, 2.5, 0],
                },
                {
                    "name": "крона_верх",
                    "geometry": "ConeGeometry",
                    "radius": 0.6,
                    "height": 1.2,
                    "segments": 8,
                    "color": "#388E3C",
                    "roughness": 0.8,
                    "position": [0, 3.3, 0],
                },
            ],
            "defaultY": 0,
        },
        "order": 2,
    },
    {
        "name": "crystal",
        "display_name": "Кристалл 💎",
        "tool_type": "create_mesh",
        "default_params": {
            "geometry": "Group",
            "children": [
                {
                    "name": "кристалл_центр",
                    "geometry": "OctahedronGeometry",
                    "radius": 0.5,
                    "color": "#9944ff",
                    "metalness": 0.8,
                    "roughness": 0.1,
                    "opacity": 0.7,
                    "transparent": True,
                    "position": [0, 0.8, 0],
                },
                {
                    "name": "кристалл_левый",
                    "geometry": "TetrahedronGeometry",
                    "radius": 0.35,
                    "color": "#bb66ff",
                    "metalness": 0.7,
                    "roughness": 0.1,
                    "opacity": 0.6,
                    "transparent": True,
                    "position": [-0.5, 0.3, 0],
                    "rotation": [0, 0, 0.3],
                },
                {
                    "name": "кристалл_правый",
                    "geometry": "TetrahedronGeometry",
                    "radius": 0.35,
                    "color": "#bb66ff",
                    "metalness": 0.7,
                    "roughness": 0.1,
                    "opacity": 0.6,
                    "transparent": True,
                    "position": [0.5, 0.3, 0],
                    "rotation": [0, 0, -0.3],
                },
                {
                    "name": "свечение",
                    "geometry": "SphereGeometry",
                    "radius": 0.15,
                    "widthSegments": 8,
                    "heightSegments": 8,
                    "color": "#ffffff",
                    "emissive": "#9944ff",
                    "opacity": 0.9,
                    "position": [0, 1.1, 0],
                },
            ],
            "defaultY": 0,
        },
        "order": 3,
    },
    {
        "name": "mushroom",
        "display_name": "Гриб 🍄",
        "tool_type": "create_mesh",
        "default_params": {
            "geometry": "Group",
            "children": [
                {
                    "name": "ножка",
                    "geometry": "CylinderGeometry",
                    "radiusTop": 0.12,
                    "radiusBottom": 0.18,
                    "height": 1.2,
                    "segments": 12,
                    "color": "#F5DEB3",
                    "roughness": 0.8,
                    "position": [0, 0.6, 0],
                },
                {
                    "name": "шляпка_низ",
                    "geometry": "CylinderGeometry",
                    "radiusTop": 0.55,
                    "radiusBottom": 0.35,
                    "height": 0.2,
                    "segments": 16,
                    "color": "#D4A574",
                    "roughness": 0.7,
                    "position": [0, 1.3, 0],
                },
                {
                    "name": "шляпка_верх",
                    "geometry": "SphereGeometry",
                    "radius": 0.55,
                    "widthSegments": 16,
                    "heightSegments": 8,
                    "phiStart": 0,
                    "phiLength": 3.14159,
                    "color": "#CC3333",
                    "roughness": 0.6,
                    "position": [0, 1.2, 0],
                },
                {
                    "name": "точка_1",
                    "geometry": "SphereGeometry",
                    "radius": 0.06,
                    "widthSegments": 6,
                    "heightSegments": 6,
                    "color": "#ffffff",
                    "position": [0.2, 1.5, 0.3],
                },
                {
                    "name": "точка_2",
                    "geometry": "SphereGeometry",
                    "radius": 0.05,
                    "widthSegments": 6,
                    "heightSegments": 6,
                    "color": "#ffffff",
                    "position": [-0.25, 1.45, -0.2],
                },
                {
                    "name": "точка_3",
                    "geometry": "SphereGeometry",
                    "radius": 0.04,
                    "widthSegments": 6,
                    "heightSegments": 6,
                    "color": "#ffffff",
                    "position": [0.1, 1.55, -0.3],
                },
            ],
            "defaultY": 0,
        },
        "order": 4,
    },
]


# ==============================================================================
# УЛЬТРА-СЛОЖНЫЕ ГРУППОВЫЕ ФИГУРЫ (ОСМЫСЛЕННЫЕ КОНСТРУКЦИИ)
# ==============================================================================

COMPLEX_TOOLS = [
    {
        "name": "well",
        "display_name": "Колодец 🪣",
        "tool_type": "create_mesh",
        "default_params": {
            "geometry": "Group",
            "children": [
                # Основание — восьмигранное кольцо из плит
                {
                    "name": "основание",
                    "geometry": "CylinderGeometry",
                    "radiusTop": 1.3,
                    "radiusBottom": 1.3,
                    "height": 0.4,
                    "segments": 8,
                    "color": "#8B7355",
                    "roughness": 0.9,
                    "position": [0, 0.2, 0],
                },
                # Стенки колодца — кольцо повыше
                {
                    "name": "стенка",
                    "geometry": "TorusGeometry",
                    "radius": 1.1,
                    "tube": 0.25,
                    "radialSegments": 8,
                    "tubularSegments": 16,
                    "color": "#A0896E",
                    "roughness": 0.85,
                    "position": [0, 0.9, 0],
                },
                # Верхнее кольцо
                {
                    "name": "верхнее_кольцо",
                    "geometry": "TorusGeometry",
                    "radius": 1.1,
                    "tube": 0.2,
                    "radialSegments": 8,
                    "tubularSegments": 16,
                    "color": "#9B8B7A",
                    "roughness": 0.8,
                    "position": [0, 1.5, 0],
                },
                # Стойка левая
                {
                    "name": "стойка_левая",
                    "geometry": "BoxGeometry",
                    "width": 0.2,
                    "height": 2.0,
                    "depth": 0.2,
                    "color": "#6B4226",
                    "roughness": 0.9,
                    "position": [-0.85, 2.0, 0],
                },
                # Стойка правая
                {
                    "name": "стойка_правая",
                    "geometry": "BoxGeometry",
                    "width": 0.2,
                    "height": 2.0,
                    "depth": 0.2,
                    "color": "#6B4226",
                    "roughness": 0.9,
                    "position": [0.85, 2.0, 0],
                },
                # Перекладина
                {
                    "name": "перекладина",
                    "geometry": "CylinderGeometry",
                    "radiusTop": 0.1,
                    "radiusBottom": 0.1,
                    "height": 1.9,
                    "segments": 8,
                    "color": "#5D4037",
                    "roughness": 0.85,
                    "position": [0, 3.1, 0],
                    "rotation": [0, 0, 1.57],
                },
                # Крыша левая
                {
                    "name": "крыша_левая",
                    "geometry": "BoxGeometry",
                    "width": 0.9,
                    "height": 0.1,
                    "depth": 1.2,
                    "color": "#A0522D",
                    "roughness": 0.8,
                    "position": [-0.45, 3.2, 0],
                    "rotation": [0, 0, 0.4],
                },
                # Крыша правая
                {
                    "name": "крыша_правая",
                    "geometry": "BoxGeometry",
                    "width": 0.9,
                    "height": 0.1,
                    "depth": 1.2,
                    "color": "#A0522D",
                    "roughness": 0.8,
                    "position": [0.45, 3.2, 0],
                    "rotation": [0, 0, -0.4],
                },
                # Ведро
                {
                    "name": "ведро",
                    "geometry": "CylinderGeometry",
                    "radiusTop": 0.2,
                    "radiusBottom": 0.15,
                    "height": 0.3,
                    "segments": 8,
                    "color": "#666666",
                    "metalness": 0.6,
                    "roughness": 0.4,
                    "position": [0, 2.0, 0.5],
                },
                # Ручка ведра
                {
                    "name": "ручка_ведра",
                    "geometry": "TorusGeometry",
                    "radius": 0.2,
                    "tube": 0.03,
                    "arc": 3.14159,
                    "color": "#555555",
                    "metalness": 0.7,
                    "roughness": 0.3,
                    "position": [0, 2.25, 0.5],
                },
            ],
            "defaultY": 0,
        },
        "order": 1,
    },
    {
        "name": "altar",
        "display_name": "Алтарь 🔮",
        "tool_type": "create_mesh",
        "default_params": {
            "geometry": "Group",
            "children": [
                # Подиум — три ступени
                {
                    "name": "ступень_1",
                    "geometry": "BoxGeometry",
                    "width": 3.0,
                    "height": 0.3,
                    "depth": 2.0,
                    "color": "#4A4A4A",
                    "roughness": 0.9,
                    "position": [0, 0.15, 0],
                },
                {
                    "name": "ступень_2",
                    "geometry": "BoxGeometry",
                    "width": 2.5,
                    "height": 0.3,
                    "depth": 1.6,
                    "color": "#3A3A3A",
                    "roughness": 0.9,
                    "position": [0, 0.45, 0],
                },
                {
                    "name": "ступень_3",
                    "geometry": "BoxGeometry",
                    "width": 2.0,
                    "height": 0.3,
                    "depth": 1.2,
                    "color": "#2A2A2A",
                    "roughness": 0.9,
                    "position": [0, 0.75, 0],
                },
                # Колонны по углам
                {
                    "name": "колонна_1",
                    "geometry": "CylinderGeometry",
                    "radiusTop": 0.12,
                    "radiusBottom": 0.12,
                    "height": 1.5,
                    "segments": 12,
                    "color": "#C8A882",
                    "roughness": 0.6,
                    "metalness": 0.2,
                    "position": [-0.8, 1.65, 0.4],
                },
                {
                    "name": "колонна_2",
                    "geometry": "CylinderGeometry",
                    "radiusTop": 0.12,
                    "radiusBottom": 0.12,
                    "height": 1.5,
                    "segments": 12,
                    "color": "#C8A882",
                    "roughness": 0.6,
                    "metalness": 0.2,
                    "position": [0.8, 1.65, 0.4],
                },
                {
                    "name": "колонна_3",
                    "geometry": "CylinderGeometry",
                    "radiusTop": 0.12,
                    "radiusBottom": 0.12,
                    "height": 1.5,
                    "segments": 12,
                    "color": "#C8A882",
                    "roughness": 0.6,
                    "metalness": 0.2,
                    "position": [-0.8, 1.65, -0.4],
                },
                {
                    "name": "колонна_4",
                    "geometry": "CylinderGeometry",
                    "radiusTop": 0.12,
                    "radiusBottom": 0.12,
                    "height": 1.5,
                    "segments": 12,
                    "color": "#C8A882",
                    "roughness": 0.6,
                    "metalness": 0.2,
                    "position": [0.8, 1.65, -0.4],
                },
                # Верхняя плита
                {
                    "name": "плита_верх",
                    "geometry": "BoxGeometry",
                    "width": 2.2,
                    "height": 0.2,
                    "depth": 1.4,
                    "color": "#3A2A1A",
                    "roughness": 0.7,
                    "metalness": 0.1,
                    "position": [0, 2.5, 0],
                },
                # Центральная сфера (магический шар)
                {
                    "name": "магический_шар",
                    "geometry": "SphereGeometry",
                    "radius": 0.3,
                    "widthSegments": 16,
                    "heightSegments": 16,
                    "color": "#8844ff",
                    "emissive": "#442288",
                    "metalness": 0.9,
                    "roughness": 0.05,
                    "opacity": 0.8,
                    "transparent": True,
                    "position": [0, 2.9, 0],
                },
                # Свечение под шаром
                {
                    "name": "свечение",
                    "geometry": "SphereGeometry",
                    "radius": 0.1,
                    "widthSegments": 8,
                    "heightSegments": 8,
                    "color": "#ffffff",
                    "emissive": "#9944ff",
                    "opacity": 0.9,
                    "position": [0, 2.55, 0],
                },
                # Свечи по бокам
                {
                    "name": "свеча_левая",
                    "geometry": "CylinderGeometry",
                    "radiusTop": 0.04,
                    "radiusBottom": 0.04,
                    "height": 0.3,
                    "segments": 8,
                    "color": "#FFF8DC",
                    "position": [-0.6, 2.55, 0.3],
                },
                {
                    "name": "огонь_левый",
                    "geometry": "ConeGeometry",
                    "radius": 0.03,
                    "height": 0.1,
                    "segments": 6,
                    "color": "#ff8833",
                    "emissive": "#ff4400",
                    "position": [-0.6, 2.75, 0.3],
                },
                {
                    "name": "свеча_правая",
                    "geometry": "CylinderGeometry",
                    "radiusTop": 0.04,
                    "radiusBottom": 0.04,
                    "height": 0.3,
                    "segments": 8,
                    "color": "#FFF8DC",
                    "position": [0.6, 2.55, 0.3],
                },
                {
                    "name": "огонь_правый",
                    "geometry": "ConeGeometry",
                    "radius": 0.03,
                    "height": 0.1,
                    "segments": 6,
                    "color": "#ff8833",
                    "emissive": "#ff4400",
                    "position": [0.6, 2.75, 0.3],
                },
            ],
            "defaultY": 0,
        },
        "order": 2,
    },
    {
        "name": "gate",
        "display_name": "Врата 🏛️",
        "tool_type": "create_mesh",
        "default_params": {
            "geometry": "Group",
            "children": [
                # Левая колонна
                {
                    "name": "колонна_л_низ",
                    "geometry": "BoxGeometry",
                    "width": 0.5,
                    "height": 1.5,
                    "depth": 0.5,
                    "color": "#D2B48C",
                    "roughness": 0.6,
                    "position": [-1.5, 0.75, 0],
                },
                {
                    "name": "колонна_л_верх",
                    "geometry": "BoxGeometry",
                    "width": 0.4,
                    "height": 2.5,
                    "depth": 0.4,
                    "color": "#C8A882",
                    "roughness": 0.6,
                    "position": [-1.5, 2.25, 0],
                },
                # Правая колонна
                {
                    "name": "колонна_п_низ",
                    "geometry": "BoxGeometry",
                    "width": 0.5,
                    "height": 1.5,
                    "depth": 0.5,
                    "color": "#D2B48C",
                    "roughness": 0.6,
                    "position": [1.5, 0.75, 0],
                },
                {
                    "name": "колонна_п_верх",
                    "geometry": "BoxGeometry",
                    "width": 0.4,
                    "height": 2.5,
                    "depth": 0.4,
                    "color": "#C8A882",
                    "roughness": 0.6,
                    "position": [1.5, 2.25, 0],
                },
                # Капители (верхушки колонн)
                {
                    "name": "капитель_л",
                    "geometry": "BoxGeometry",
                    "width": 0.7,
                    "height": 0.3,
                    "depth": 0.7,
                    "color": "#FFD700",
                    "metalness": 0.8,
                    "roughness": 0.2,
                    "position": [-1.5, 3.6, 0],
                },
                {
                    "name": "капитель_п",
                    "geometry": "BoxGeometry",
                    "width": 0.7,
                    "height": 0.3,
                    "depth": 0.7,
                    "color": "#FFD700",
                    "metalness": 0.8,
                    "roughness": 0.2,
                    "position": [1.5, 3.6, 0],
                },
                # Архитрав (горизонтальная балка)
                {
                    "name": "архитрав",
                    "geometry": "BoxGeometry",
                    "width": 3.5,
                    "height": 0.4,
                    "depth": 0.6,
                    "color": "#FFD700",
                    "metalness": 0.7,
                    "roughness": 0.3,
                    "position": [0, 3.9, 0],
                },
                # Фронтон (треугольник сверху)
                {
                    "name": "фронтон_центр",
                    "geometry": "ConeGeometry",
                    "radius": 0.0,
                    "radiusBottom": 0.0,
                    "height": 0.0,
                    "segments": 3,
                    "color": "#FFD700",
                    "metalness": 0.6,
                    "roughness": 0.3,
                    "position": [0, 4.2, 0],
                    "scale_override": [2.0, 1.2, 0.8],
                },
                # Заменяем конус на коробку для фронтона (проще)
                {
                    "name": "фронтон",
                    "geometry": "BoxGeometry",
                    "width": 2.0,
                    "height": 0.8,
                    "depth": 0.6,
                    "color": "#FFD700",
                    "metalness": 0.6,
                    "roughness": 0.3,
                    "position": [0, 4.3, 0],
                },
                # Декоративный шар на вершине
                {
                    "name": "шар_вершина",
                    "geometry": "SphereGeometry",
                    "radius": 0.2,
                    "widthSegments": 12,
                    "heightSegments": 12,
                    "color": "#FFD700",
                    "metalness": 0.9,
                    "roughness": 0.1,
                    "position": [0, 5.0, 0],
                },
                # Боковые украшения
                {
                    "name": "украшение_л",
                    "geometry": "SphereGeometry",
                    "radius": 0.15,
                    "widthSegments": 8,
                    "heightSegments": 8,
                    "color": "#FFD700",
                    "metalness": 0.8,
                    "position": [-1.0, 4.3, 0.5],
                },
                {
                    "name": "украшение_п",
                    "geometry": "SphereGeometry",
                    "radius": 0.15,
                    "widthSegments": 8,
                    "heightSegments": 8,
                    "color": "#FFD700",
                    "metalness": 0.8,
                    "position": [1.0, 4.3, 0.5],
                },
            ],
            "defaultY": 0,
        },
        "order": 3,
    },
    {
        "name": "lamp_post",
        "display_name": "Фонарь 🏮",
        "tool_type": "create_mesh",
        "default_params": {
            "geometry": "Group",
            "children": [
                # Основание
                {
                    "name": "основание",
                    "geometry": "CylinderGeometry",
                    "radiusTop": 0.4,
                    "radiusBottom": 0.5,
                    "height": 0.3,
                    "segments": 12,
                    "color": "#2C2C2C",
                    "metalness": 0.7,
                    "roughness": 0.4,
                    "position": [0, 0.15, 0],
                },
                # Столб
                {
                    "name": "столб_низ",
                    "geometry": "CylinderGeometry",
                    "radiusTop": 0.12,
                    "radiusBottom": 0.15,
                    "height": 1.5,
                    "segments": 12,
                    "color": "#3A3A3A",
                    "metalness": 0.6,
                    "roughness": 0.5,
                    "position": [0, 1.05, 0],
                },
                {
                    "name": "столб_верх",
                    "geometry": "CylinderGeometry",
                    "radiusTop": 0.08,
                    "radiusBottom": 0.12,
                    "height": 1.5,
                    "segments": 12,
                    "color": "#3A3A3A",
                    "metalness": 0.6,
                    "roughness": 0.5,
                    "position": [0, 2.55, 0],
                },
                # Кронштейн
                {
                    "name": "кронштейн",
                    "geometry": "TorusGeometry",
                    "radius": 0.25,
                    "tube": 0.05,
                    "radialSegments": 8,
                    "tubularSegments": 12,
                    "color": "#4A4A4A",
                    "metalness": 0.8,
                    "roughness": 0.3,
                    "position": [0, 3.3, 0],
                },
                # Корпус фонаря
                {
                    "name": "корпус_фонаря",
                    "geometry": "CylinderGeometry",
                    "radiusTop": 0.2,
                    "radiusBottom": 0.25,
                    "height": 0.6,
                    "segments": 8,
                    "color": "#FFD700",
                    "metalness": 0.9,
                    "roughness": 0.1,
                    "position": [0, 3.6, 0],
                },
                # Стекло (полупрозрачное)
                {
                    "name": "стекло",
                    "geometry": "CylinderGeometry",
                    "radiusTop": 0.18,
                    "radiusBottom": 0.23,
                    "height": 0.5,
                    "segments": 12,
                    "color": "#FFFFCC",
                    "emissive": "#FFAA00",
                    "opacity": 0.5,
                    "transparent": True,
                    "metalness": 0.1,
                    "roughness": 0.2,
                    "position": [0, 3.6, 0],
                },
                # Крышка
                {
                    "name": "крышка",
                    "geometry": "ConeGeometry",
                    "radius": 0.25,
                    "height": 0.3,
                    "segments": 8,
                    "color": "#2C2C2C",
                    "metalness": 0.8,
                    "roughness": 0.3,
                    "position": [0, 3.95, 0],
                },
                # Шпиль
                {
                    "name": "шпиль",
                    "geometry": "CylinderGeometry",
                    "radiusTop": 0.02,
                    "radiusBottom": 0.04,
                    "height": 0.3,
                    "segments": 6,
                    "color": "#FFD700",
                    "metalness": 0.9,
                    "position": [0, 4.2, 0],
                },
                # Светящийся шар внутри
                {
                    "name": "лампа",
                    "geometry": "SphereGeometry",
                    "radius": 0.08,
                    "widthSegments": 8,
                    "heightSegments": 8,
                    "color": "#FFFFFF",
                    "emissive": "#FFAA00",
                    "opacity": 0.9,
                    "position": [0, 3.6, 0],
                },
            ],
            "defaultY": 0,
        },
        "order": 4,
    },
]


# ==============================================================================
# НАБОРЫ ИНСТРУМЕНТОВ
# ==============================================================================

TOOLKITS = [
    {
        "name": "Базовые фигуры",
        "icon": "📐",
        "description": "Куб, сфера, цилиндр, конус, пирамида, тор, плоскость",
        "order": 1,
        "tool_names": [
            "cube",
            "sphere",
            "cylinder",
            "cone",
            "pyramid",
            "torus",
            "plane",
        ],
    },
    {
        "name": "Платоновы тела",
        "icon": "🔮",
        "description": "Тетраэдр, октаэдр, икосаэдр, додекаэдр",
        "order": 2,
        "tool_names": [
            "tetrahedron",
            "octahedron",
            "icosahedron",
            "dodecahedron",
        ],
    },
    {
        "name": "Экзотика",
        "icon": "🌀",
        "description": "Торический узел, капсула, кольцо, диск, каркасный куб",
        "order": 3,
        "tool_names": [
            "torus_knot",
            "capsule",
            "ring",
            "disc",
            "wireframe_cube",
        ],
    },
    {
        "name": "Фигуры вращения",
        "icon": "🏺",
        "description": "Ваза, яйцо",
        "order": 4,
        "tool_names": [
            "vase",
            "egg",
        ],
    },
    {
        "name": "Строительные блоки",
        "icon": "🧱",
        "description": "Плита, колонна, арка, ступенька",
        "order": 5,
        "tool_names": [
            "slab",
            "pillar",
            "arch",
            "step",
        ],
    },
    {
        "name": "Органика и формы",
        "icon": "🌿",
        "description": "Сердце, звезда, дерево, кристалл, гриб",
        "order": 6,
        "tool_names": [
            "heart",
            "star",
            "tree_simple",
            "crystal",
            "mushroom",
        ],
    },
    {
        "name": "Сложные конструкции",
        "icon": "🏗️",
        "description": "Колодец, алтарь, врата, фонарь",
        "order": 7,
        "tool_names": [
            "well",
            "altar",
            "gate",
            "lamp_post",
        ],
    },
    {
        "name": "Освещение",
        "icon": "💡",
        "description": "Точечный свет, прожектор, факел",
        "order": 8,
        "tool_names": [
            "point_light",
            "spot_light",
            "torch_light",
        ],
    },
]


# ==============================================================================
# КОМАНДА ЗАГРУЗКИ
# ==============================================================================


class Command(BaseCommand):
    help = "Загружает ВСЕ инструменты и создаёт стартовые наборы"

    def handle(self, *args, **options):
        # ======================================================================
        # 1. СОЗДАЁМ ИНСТРУМЕНТЫ В РЕЕСТРЕ
        # ======================================================================
        all_tools_data = ALL_TOOLS + GROUP_TOOLS + COMPLEX_TOOLS

        created_tools = 0
        updated_tools = 0

        for tool_data in all_tools_data:
            obj, was_created = Tool.objects.update_or_create(
                name=tool_data["name"],
                defaults=tool_data,
            )
            if was_created:
                created_tools += 1
                self.stdout.write(
                    self.style.SUCCESS(f"  ✅ Инструмент: {obj.display_name}")
                )
            else:
                updated_tools += 1
                self.stdout.write(
                    self.style.WARNING(f"  🔄 Инструмент обновлён: {obj.display_name}")
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\n📦 Инструменты: создано {created_tools}, обновлено {updated_tools}. "
                f"Всего: {created_tools + updated_tools}"
            )
        )

        # ======================================================================
        # 2. СОЗДАЁМ НАБОРЫ
        # ======================================================================

        # Берём первого суперпользователя как владельца наборов
        owner = User.objects.filter(is_superuser=True).first()
        if not owner:
            owner = User.objects.first()

        if not owner:
            self.stdout.write(
                self.style.ERROR(
                    "❌ Нет пользователей в системе! Создайте суперпользователя."
                )
            )
            return

        created_toolkits = 0
        updated_toolkits = 0

        for toolkit_data in TOOLKITS:
            tool_names = toolkit_data.pop("tool_names")
            tools = Tool.objects.filter(name__in=tool_names)

            toolkit, was_created = Toolkit.objects.update_or_create(
                name=toolkit_data["name"],
                defaults={
                    **toolkit_data,
                    "owner": owner,
                },
            )

            # Наполняем набор инструментами
            toolkit.tools.set(tools)

            if was_created:
                created_toolkits += 1
                self.stdout.write(
                    self.style.SUCCESS(f"  ✅ Набор: {toolkit.icon} {toolkit.name}")
                )
            else:
                updated_toolkits += 1
                self.stdout.write(
                    self.style.WARNING(
                        f"  🔄 Набор обновлён: {toolkit.icon} {toolkit.name}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\n🧰 Наборы: создано {created_toolkits}, обновлено {updated_toolkits}. "
                f"Всего: {created_toolkits + updated_toolkits}"
            )
        )

        self.stdout.write(
            self.style.SUCCESS("\n🎉 Готово! Запустите сервер и открывайте редактор.")
        )
