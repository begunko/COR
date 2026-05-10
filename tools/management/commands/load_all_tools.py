from django.core.management.base import BaseCommand
from tools.models import Tool

ALL_TOOLS = [
    # ===== БАЗОВЫЕ =====
    {
        "name": "cube",
        "display_name": "Куб",
        "tool_type": "create_mesh",
        "default_params": {
            "geometry": "BoxGeometry",
            "size": 1,
            "color": "#ff6600",
            "defaultY": 0.5,
        },
        "order": 1,
        "available_for_all": True,
    },
    {
        "name": "sphere",
        "display_name": "Сфера",
        "tool_type": "create_mesh",
        "default_params": {
            "geometry": "SphereGeometry",
            "radius": 0.5,
            "color": "#3388ff",
            "defaultY": 0.5,
        },
        "order": 2,
        "available_for_all": True,
    },
    {
        "name": "cylinder",
        "display_name": "Цилиндр",
        "tool_type": "create_mesh",
        "default_params": {
            "geometry": "CylinderGeometry",
            "radius": 0.5,
            "height": 1.5,
            "color": "#00cc44",
            "defaultY": 0.75,
        },
        "order": 3,
        "available_for_all": True,
    },
    {
        "name": "cone",
        "display_name": "Конус",
        "tool_type": "create_mesh",
        "default_params": {
            "geometry": "ConeGeometry",
            "radius": 0.5,
            "height": 1.5,
            "color": "#ffcc00",
            "defaultY": 0.75,
        },
        "order": 4,
        "available_for_all": True,
    },
    {
        "name": "pyramid",
        "display_name": "Пирамида",
        "tool_type": "create_mesh",
        "default_params": {
            "geometry": "ConeGeometry",
            "radius": 1,
            "height": 1.5,
            "radialSegments": 4,
            "color": "#cc33ff",
            "defaultY": 0.75,
        },
        "order": 5,
        "available_for_all": True,
    },
    {
        "name": "torus",
        "display_name": "Тор",
        "tool_type": "create_mesh",
        "default_params": {
            "geometry": "TorusGeometry",
            "radius": 0.7,
            "tube": 0.3,
            "color": "#ff8833",
            "defaultY": 1,
        },
        "order": 6,
        "available_for_all": True,
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
            "defaultY": 0,
        },
        "order": 7,
        "available_for_all": True,
    },
    # ===== ПЛАТОНОВЫ ТЕЛА =====
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
        "order": 8,
        "available_for_all": True,
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
        "order": 9,
        "available_for_all": True,
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
        "order": 10,
        "available_for_all": True,
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
        "order": 11,
        "available_for_all": True,
    },
    # ===== ЭКЗОТИКА =====
    {
        "name": "torus_knot",
        "display_name": "Торический узел",
        "tool_type": "create_mesh",
        "default_params": {
            "geometry": "TorusKnotGeometry",
            "radius": 0.8,
            "tube": 0.2,
            "color": "#44ffcc",
            "defaultY": 1.5,
        },
        "order": 12,
        "available_for_all": True,
    },
    {
        "name": "capsule",
        "display_name": "Капсула",
        "tool_type": "create_mesh",
        "default_params": {
            "geometry": "CapsuleGeometry",
            "radius": 0.3,
            "length": 1.5,
            "color": "#ff44cc",
            "defaultY": 0.75,
        },
        "order": 13,
        "available_for_all": True,
    },
    {
        "name": "ring",
        "display_name": "Кольцо",
        "tool_type": "create_mesh",
        "default_params": {
            "geometry": "RingGeometry",
            "innerRadius": 0.5,
            "outerRadius": 1,
            "color": "#cccc44",
            "defaultY": 0.5,
        },
        "order": 14,
        "available_for_all": True,
    },
    {
        "name": "circle",
        "display_name": "Диск",
        "tool_type": "create_mesh",
        "default_params": {
            "geometry": "CircleGeometry",
            "radius": 1,
            "color": "#cccccc",
            "defaultY": 0,
        },
        "order": 15,
        "available_for_all": True,
    },
    {
        "name": "lathe_vase",
        "display_name": "Ваза",
        "tool_type": "create_mesh",
        "default_params": {
            "geometry": "LatheGeometry",
            "profile": "vase",
            "color": "#ffaa44",
            "defaultY": 0.5,
        },
        "order": 16,
        "available_for_all": True,
    },
    {
        "name": "lathe_egg",
        "display_name": "Яйцо",
        "tool_type": "create_mesh",
        "default_params": {
            "geometry": "LatheGeometry",
            "profile": "egg",
            "color": "#ffffff",
            "defaultY": 0.6,
        },
        "order": 17,
        "available_for_all": True,
    },
    # ===== ФОРМЫ =====
    {
        "name": "shape_heart",
        "display_name": "Сердце ❤️",
        "tool_type": "create_mesh",
        "default_params": {
            "geometry": "ShapeGeometry",
            "shape": "heart",
            "extrudeDepth": 0.2,
            "color": "#ff2244",
            "defaultY": 0.6,
        },
        "order": 18,
        "available_for_all": True,
    },
    {
        "name": "shape_star",
        "display_name": "Звезда ⭐",
        "tool_type": "create_mesh",
        "default_params": {
            "geometry": "ShapeGeometry",
            "shape": "star",
            "extrudeDepth": 0.2,
            "color": "#ffdd00",
            "defaultY": 0.6,
        },
        "order": 19,
        "available_for_all": True,
    },
    # ===== РАЗНОЕ =====
    {
        "name": "box_wide",
        "display_name": "Плита",
        "tool_type": "create_mesh",
        "default_params": {
            "geometry": "BoxGeometry",
            "width": 3,
            "height": 0.2,
            "depth": 2,
            "color": "#8B7355",
            "defaultY": 0.1,
        },
        "order": 20,
        "available_for_all": True,
    },
    {
        "name": "pillar",
        "display_name": "Колонна",
        "tool_type": "create_mesh",
        "default_params": {
            "geometry": "CylinderGeometry",
            "radius": 0.3,
            "height": 3,
            "color": "#D2B48C",
            "defaultY": 1.5,
        },
        "order": 21,
        "available_for_all": True,
    },
    {
        "name": "wireframe_cube",
        "display_name": "Каркасный куб",
        "tool_type": "create_mesh",
        "default_params": {
            "geometry": "BoxGeometry",
            "size": 1,
            "color": "#00ff88",
            "wireframe": True,
            "defaultY": 0.5,
        },
        "order": 22,
        "available_for_all": True,
    },
]


class Command(BaseCommand):
    help = "Загружает ВСЕ инструменты-меши в базу данных"

    def handle(self, *args, **options):
        created = 0
        updated = 0

        for tool_data in ALL_TOOLS:
            obj, was_created = Tool.objects.update_or_create(
                name=tool_data["name"], defaults=tool_data
            )
            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f"  ✅ {obj.display_name}"))
            else:
                updated += 1
                self.stdout.write(
                    self.style.WARNING(f"  🔄 {obj.display_name} (обновлён)")
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\n🎉 Готово! Создано: {created}, обновлено: {updated}. Всего инструментов: {created + updated}"
            )
        )
