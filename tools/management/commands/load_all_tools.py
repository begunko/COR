# tools/management/commands/load_all_tools.py
import json
import os
from pathlib import Path
from django.core.management.base import BaseCommand
from tools.models import Tool, Toolkit
from users.models import User


class Command(BaseCommand):
    help = "Рекурсивно загружает все наборы инструментов из JSON-файлов в fixtures/ и поддиректориях."

    FIXTURES_DIR = "management/commands/fixtures"

    # Разрешённые поля для модели Toolkit (исключаем version, tool_names и прочее)
    ALLOWED_TOOLKIT_FIELDS = {"name", "icon", "description", "order", "owner", "tools"}

    def handle(self, *args, **options):
        app_dir = Path(__file__).resolve().parent.parent.parent
        fixtures_path = app_dir / self.FIXTURES_DIR

        if not fixtures_path.exists():
            self.stdout.write(
                self.style.ERROR(
                    f"❌ Директория с фикстурами не найдена: {fixtures_path}"
                )
            )
            return

        owner = User.objects.filter(is_superuser=True).first() or User.objects.first()
        if not owner:
            self.stdout.write(
                self.style.ERROR(
                    "❌ В системе нет пользователей! Создайте суперпользователя."
                )
            )
            return

        total_tools_created = 0
        total_toolkits_created = 0
        global_tool_registry = {}

        json_files = sorted(fixtures_path.rglob("*.json"))

        for json_file in json_files:
            relative_path = json_file.relative_to(fixtures_path)
            self.stdout.write(
                self.style.NOTICE(f"\n📂 Обрабатывается: {relative_path}")
            )

            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except json.JSONDecodeError as e:
                self.stdout.write(self.style.ERROR(f"   ❌ Ошибка чтения JSON: {e}"))
                continue

            # --- Часть 1: Загрузка инструментов ---
            file_tool_ids = []
            if "tools" in data:
                for tool_data in data["tools"]:
                    # Удаляем лишние поля, которых нет в модели Tool
                    tool_data.pop("toolkits", None)
                    tool_data.pop("version", None)

                    obj, created = Tool.objects.update_or_create(
                        name=tool_data["name"], defaults=tool_data
                    )
                    file_tool_ids.append(obj.id)
                    global_tool_registry[obj.name] = obj.id

                    if created:
                        self.stdout.write(
                            self.style.SUCCESS(f"   ✅ Создан: {obj.display_name}")
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(f"   🔄 Обновлён: {obj.display_name}")
                        )
                    total_tools_created += 1

            # --- Часть 2: Загрузка набора ---
            if "toolkit" in data:
                toolkit_data = data["toolkit"]
                tool_names_from_toolkit = toolkit_data.pop("tool_names", [])

                # Удаляем лишние поля из данных набора
                toolkit_data.pop("version", None)

                # Оставляем только разрешённые поля для Toolkit
                clean_toolkit_data = {
                    key: value
                    for key, value in toolkit_data.items()
                    if key in self.ALLOWED_TOOLKIT_FIELDS
                }

                toolkit, tk_created = Toolkit.objects.update_or_create(
                    name=clean_toolkit_data["name"],
                    defaults={**clean_toolkit_data, "owner": owner},
                )

                ids_to_set = list(file_tool_ids)

                if tool_names_from_toolkit:
                    for name in tool_names_from_toolkit:
                        if name in global_tool_registry:
                            ids_to_set.append(global_tool_registry[name])
                        else:
                            try:
                                tool = Tool.objects.get(name=name)
                                ids_to_set.append(tool.id)
                                global_tool_registry[name] = tool.id
                            except Tool.DoesNotExist:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f"   ⚠️ Инструмент '{name}' не найден в реестре!"
                                    )
                                )

                toolkit.tools.set(ids_to_set)

                if tk_created:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"   📦 Создан набор: {clean_toolkit_data.get('icon', '')} {clean_toolkit_data['name']}"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"   🔄 Обновлён набор: {clean_toolkit_data.get('icon', '')} {clean_toolkit_data['name']}"
                        )
                    )
                total_toolkits_created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\n🎉 ИТОГО: Создано/обновлено инструментов: {total_tools_created}, наборов: {total_toolkits_created}"
            )
        )
