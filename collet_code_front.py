#!/usr/bin/env python3
"""
Сборщик кода интерфейса COR Engine (только static и templates).
Игнорирует Python-файлы, миграции, настройки и прочий бэкенд.
Собирает только HTML, CSS, JS — всё, что относится к фронтенду.
"""

import os
from pathlib import Path
from datetime import datetime


def collect_frontend_code(project_path=".", output_file="COR_frontend_code.txt"):
    """Собирает содержимое папок static/ и templates/ в один текстовый файл"""

    # === ЦЕЛЕВЫЕ ПАПКИ ===
    target_dirs = ["static", "templates"]

    # === ИСКЛЮЧАЕМЫЕ ИЗ ЦЕЛЕВЫХ ПАПОК ===
    exclude_files = {
        "admin.css",  # это JS, а не CSS (историческое)
    }

    exclude_extensions = {
        # Изображения
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".svg",
        ".ico",
        ".webp",
        # Шрифты
        ".woff",
        ".woff2",
        ".ttf",
        ".eot",
        ".otf",
        # Минифицированные (нечитаемые)
        ".min.js",
        ".min.css",
        # Карты
        ".map",
    }

    all_files = []
    skipped_count = 0

    print("🔍 Сканирую только папки static/ и templates/...")

    for target in target_dirs:
        target_path = Path(project_path) / target
        if not target_path.exists():
            print(f"  ⚠️  Папка не найдена: {target}")
            continue

        for root, dirs, files in os.walk(target_path):
            for file in sorted(files):
                file_path = Path(root) / file
                extension = file_path.suffix.lower()

                # Проверка на исключаемые файлы и расширения
                if file in exclude_files:
                    skipped_count += 1
                    continue
                if extension in exclude_extensions:
                    skipped_count += 1
                    continue
                if file_path.stat().st_size == 0:
                    skipped_count += 1
                    continue

                all_files.append(file_path)

    all_files.sort()

    print(f"📝 Записываю {len(all_files)} файлов в {output_file}...")

    total_lines = 0
    processed_files = 0

    with open(output_file, "w", encoding="utf-8") as out:
        # Заголовок
        out.write("=" * 80 + "\n")
        out.write("ПРОЕКТ: COR (Frontend)\n")
        out.write(
            f"Дата создания отчёта: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )
        out.write(f"Исключено бинарных/минифицированных файлов: {skipped_count}\n")
        out.write("=" * 80 + "\n\n")

        # Оглавление
        out.write("📑 СОДЕРЖАНИЕ (ИНТЕРФЕЙС)\n")
        out.write("-" * 80 + "\n")
        for f in all_files:
            try:
                # Показываем путь, начиная с папки static или templates
                rel_path_parts = f.relative_to(project_path).parts
                if rel_path_parts[0] in target_dirs:
                    display_path = (
                        Path(*rel_path_parts[1:])
                        if len(rel_path_parts) > 1
                        else Path(rel_path_parts[0])
                    )
                else:
                    display_path = f.relative_to(project_path)

                size_kb = f.stat().st_size / 1024
                out.write(f"  {display_path} ({size_kb:.1f} KB)\n")
            except:
                pass

        out.write("\n" + "=" * 80 + "\n")
        out.write("📄 ИСХОДНЫЙ КОД ФАЙЛОВ\n")
        out.write("=" * 80 + "\n")

        # Содержимое
        for f in all_files:
            try:
                rel_path = f.relative_to(project_path)
                with open(f, "r", encoding="utf-8") as inf:
                    content = inf.read()
                    if not content.strip():
                        skipped_count += 1
                        continue

                out.write("\n\n" + "🟢 " + "=" * 76 + "\n")
                out.write(f"📍 ПУТЬ: {rel_path}\n")
                out.write(f"📄 ФАЙЛ: {f.name}\n")
                out.write(
                    f"📊 РАЗМЕР: {f.stat().st_size / 1024:.1f} KB | СТРОК: {len(content.splitlines())}\n"
                )
                out.write("=" * 80 + "\n\n")
                out.write(content)
                if not content.endswith("\n"):
                    out.write("\n")

                total_lines += len(content.splitlines())
                processed_files += 1
                print(f"  ✅ {rel_path}")

            except Exception as e:
                print(f"  ❌ Ошибка в {f.name}: {e}")

    print("\n" + "=" * 80)
    print("📊 ГОТОВО!")
    print(f"✅ Файлов интерфейса: {processed_files}")
    print(f"📝 Строк кода: {total_lines}")
    print(f"💾 Размер отчёта: {Path(output_file).stat().st_size / 1024:.1f} KB")
    print(f"📁 Сохранён в: {output_file}")


if __name__ == "__main__":
    if Path("manage.py").exists():
        print("🚀 Сборка фронтенда COR Engine...\n")
        collect_frontend_code()
    else:
        print("❌ Ошибка: скрипт нужно запускать из корня проекта (рядом с manage.py)")
