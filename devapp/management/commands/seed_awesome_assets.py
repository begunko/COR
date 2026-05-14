# assets/management/commands/seed_awesome_assets.py
import json
from pathlib import Path
from django.core.management.base import BaseCommand
from assets.models import Asset
from users.models import User


class Command(BaseCommand):
    help = "Загружает готовые сцены-ассеты из JSON-файлов в директории awesome_scenes/"

    SCENES_DIR = Path(__file__).resolve().parent / "awesome_scenes"

    def handle(self, *args, **options):
        if not self.SCENES_DIR.exists():
            self.stdout.write(
                self.style.ERROR(
                    f"❌ Папка со сценами не найдена: {self.SCENES_DIR}\n"
                    f"   Создайте её и поместите туда JSON-файлы сцен."
                )
            )
            return

        owner = User.objects.filter(is_superuser=True).first() or User.objects.first()
        if not owner:
            self.stdout.write(
                self.style.ERROR("❌ Нет пользователей! Создайте суперпользователя.")
            )
            return

        json_files = sorted(self.SCENES_DIR.rglob("*.json"))

        if not json_files:
            self.stdout.write(
                self.style.WARNING("⚠️  В папке awesome_scenes/ нет JSON-файлов.")
            )
            return

        total_created = 0
        total_updated = 0
        total_errors = 0

        self.stdout.write(self.style.NOTICE(f"\n📂 Найдено сцен: {len(json_files)}\n"))

        for json_file in json_files:
            relative_path = json_file.relative_to(self.SCENES_DIR)

            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    scene_data = json.load(f)
            except json.JSONDecodeError as e:
                self.stdout.write(
                    self.style.ERROR(f"   ❌ Ошибка JSON в {relative_path}: {e}")
                )
                total_errors += 1
                continue
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"   ❌ Ошибка чтения {relative_path}: {e}")
                )
                total_errors += 1
                continue

            name = scene_data.get("name")
            if not name:
                self.stdout.write(
                    self.style.ERROR(
                        f"   ❌ В файле {relative_path} отсутствует поле 'name'"
                    )
                )
                total_errors += 1
                continue

            if "data" not in scene_data:
                self.stdout.write(
                    self.style.ERROR(
                        f"   ❌ В файле {relative_path} отсутствует поле 'data'"
                    )
                )
                total_errors += 1
                continue

            # Определяем категорию из пути (для логирования)
            parent_dir = relative_path.parent
            category = (
                parent_dir.name
                if parent_dir.name and parent_dir.name != "."
                else "general"
            )

            # ============================================================
            # ИСПРАВЛЕНИЕ: собираем ТОЛЬКО поля, которые есть в модели Asset
            # ============================================================
            defaults = {
                "description": scene_data.get("description", ""),
                "data": scene_data.get("data", {}),
                "animation": scene_data.get("animation", {}),
                "tags": scene_data.get("tags", []),
                "created_by": owner,
            }
            # Поле category убрано из defaults, т.к. его нет в модели

            try:
                obj, was_created = Asset.objects.update_or_create(
                    name=name,
                    defaults=defaults,
                )

                if was_created:
                    total_created += 1
                    self.stdout.write(self.style.SUCCESS(f"   ✅ [{category}] {name}"))
                else:
                    total_updated += 1
                    self.stdout.write(
                        self.style.WARNING(f"   🔄 [{category}] {name} (обновлён)")
                    )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"   ❌ Ошибка сохранения {name}: {e}")
                )
                total_errors += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\n{'=' * 60}\n"
                f"🎉 ИТОГО:\n"
                f"   ✅ Создано:    {total_created}\n"
                f"   🔄 Обновлено:  {total_updated}\n"
                f"   ❌ Ошибок:     {total_errors}\n"
                f"   📂 Категорий:  {len(set(f.relative_to(self.SCENES_DIR).parent.name for f in json_files if f.relative_to(self.SCENES_DIR).parent.name != '.'))}\n"
                f"{'=' * 60}"
            )
        )
