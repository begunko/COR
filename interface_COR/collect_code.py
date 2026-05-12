#!/usr/bin/env python3
"""
Универсальный сборщик кода проекта в один текстовый файл.
Автоматически собирает ВЕСЬ код из любой папки, где находится скрипт.
Исключает служебные, бинарные и автоматически сгенерированные файлы.
"""

import os
from pathlib import Path
from datetime import datetime


def collect_all_code(output_file=None):
    """Собирает содержимое всех файлов с кодом в один текстовый файл"""

    # Определяем папку, где лежит скрипт
    script_dir = Path(__file__).parent.resolve()
    project_path = script_dir

    # Имя папки проекта (без пробелов и спецсимволов)
    project_name = project_path.name.replace(" ", "_").replace("-", "_")

    # Если имя выходного файла не задано, формируем автоматически
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = project_path / f"CODE_{project_name}_{timestamp}.txt"
    else:
        output_file = project_path / output_file

    # === ИСКЛЮЧАЕМЫЕ ДИРЕКТОРИИ ===
    exclude_dirs = {
        # Python
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        # Git
        ".git",
        # Виртуальные окружения
        "venv",
        "env",
        ".venv",
        "ENV",
        ".pixi",
        # Зависимости
        "node_modules",
        # Django
        "staticfiles",
        "migrations",
        ".webassets-cache",
        # IDE
        ".idea",
        ".vscode",
        ".vs",
        ".spyproject",
        ".spyderproject",
        ".ropeproject",
        # Сборка и дистрибуция
        "build",
        "dist",
        "eggs",
        "develop-eggs",
        ".eggs",
        "parts",
        "sdist",
        "var",
        # Документация
        "docs/_build",
        "site",
        # Прочие
        ".tox",
        ".nox",
        ".hypothesis",
        "management",
        "vendor",
    }

    # === ИСКЛЮЧАЕМЫЕ ФАЙЛЫ ===
    exclude_files = {
        # Сам скрипт (по любому имени)
        Path(__file__).name,
        # Git
        ".gitignore",
        ".gitattributes",
        ".gitmodules",
        # Лицензии
        "LICENSE",
        "LICENSE.txt",
        "LICENSE.md",
        "LICENCE",
        # Системные
        ".DS_Store",
        "Thumbs.db",
        "desktop.ini",
        # Базы данных
        "*.sqlite3",
        "*.db",
        "db.sqlite3-journal",
        # Логи и временные
        "*.log",
        "pip-log.txt",
        # Блокировки
        "*.lock",
        ".installed.cfg",
        # Бэкапы
        "*~",
        "*.bak",
        "*.backup",
        "*.old",
    }

    # === ИСКЛЮЧАЕМЫЕ РАСШИРЕНИЯ ===
    exclude_extensions = {
        # Скомпилированный Python
        ".pyc",
        ".pyo",
        ".pyd",
        # Базы данных
        ".sqlite3",
        ".db",
        ".sqlite",
        ".sqlite3-journal",
        # Логи
        ".log",
        # Изображения
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".svg",
        ".ico",
        ".webp",
        ".tiff",
        ".tif",
        ".raw",
        ".cr2",
        ".nef",
        ".psd",
        # Шрифты
        ".woff",
        ".woff2",
        ".ttf",
        ".eot",
        ".otf",
        # Минифицированные
        ".min.js",
        ".min.css",
        # Source maps
        ".map",
        # Скомпилированные/бинарные
        ".so",
        ".dll",
        ".dylib",
        ".exe",
        ".bin",
        # Архивы
        ".zip",
        ".tar",
        ".gz",
        ".bz2",
        ".xz",
        ".7z",
        ".rar",
        # Документы
        ".pdf",
        ".doc",
        ".docx",
        ".xls",
        ".xlsx",
        ".ppt",
        ".pptx",
        # Аудио
        ".mp3",
        ".wav",
        ".ogg",
        ".flac",
        ".aac",
        ".wma",
        ".m4a",
        # Видео
        ".mp4",
        ".avi",
        ".mov",
        ".mkv",
        ".wmv",
        ".flv",
        ".webm",
        # 3D модели
        ".fbx",
        ".glb",
        ".gltf",
        ".blend",
        ".obj",
        ".3ds",
        ".max",
        # Кэш и временные
        ".cache",
        ".tmp",
        ".temp",
        ".swp",
        ".swo",
        # Сертификаты и ключи
        ".pem",
        ".key",
        ".crt",
        ".cert",
        # Виртуальные машины и контейнеры
        ".iso",
        ".img",
        ".vmdk",
        ".qcow2",
    }

    all_files = []
    skipped_count = 0
    skipped_files_list = []

    print("\n" + "=" * 60)
    print("🔍 УНИВЕРСАЛЬНЫЙ СБОРЩИК КОДА")
    print("=" * 60)
    print(f"📁 Папка проекта: {project_path}")
    print(f"📄 Выходной файл: {output_file.name}")
    print()

    # Собираем список файлов
    for root, dirs, files in os.walk(project_path):
        current_path = Path(root)

        # Пропускаем папку, если она в исключениях
        dirs_to_remove = []
        for d in dirs:
            if d in exclude_dirs or d.startswith("."):
                dirs_to_remove.append(d)

        for d in dirs_to_remove:
            dirs.remove(d)
            print(f"  ⏭️  Пропущена директория: {d}/")

        # Обрабатываем файлы
        for file in sorted(files):
            file_path = current_path / file
            file_lower = file.lower()
            extension = file_path.suffix.lower()

            # Пропускаем выходной файл (предыдущие сборки)
            if file_path.name == output_file.name:
                skipped_count += 1
                skipped_files_list.append(f"{file} (выходной файл сборки)")
                continue

            # Проверка по точному имени файла
            if file in exclude_files or file_lower in exclude_files:
                skipped_count += 1
                skipped_files_list.append(f"{file} (по имени файла)")
                continue

            # Проверка по расширению
            if extension in exclude_extensions:
                skipped_count += 1
                skipped_files_list.append(f"{file} (расширение {extension})")
                continue

            # Проверка по паттернам с wildcards
            skip_by_pattern = False
            for pattern in exclude_files:
                if pattern.startswith("*") and file_lower.endswith(pattern[1:].lower()):
                    skip_by_pattern = True
                    skipped_count += 1
                    skipped_files_list.append(f"{file} (паттерн {pattern})")
                    break
            if skip_by_pattern:
                continue

            # Проверка размера
            try:
                size = file_path.stat().st_size
                if size == 0:
                    skipped_count += 1
                    skipped_files_list.append(f"{file} (пустой файл)")
                    continue
                if size > 10 * 1024 * 1024:  # > 10MB
                    print(f"  ⚠️  Пропущен большой файл: {file} ({size // 1024}KB)")
                    skipped_count += 1
                    continue
            except:
                continue

            all_files.append(file_path)

    # Сортируем
    all_files.sort()

    # Показываем пропущенные файлы
    if skipped_files_list:
        print(f"\n📋 Пропущено файлов: {len(skipped_files_list)}")
        for sf in skipped_files_list[:5]:
            print(f"   • {sf}")
        if len(skipped_files_list) > 5:
            print(f"   ... и ещё {len(skipped_files_list) - 5}")

    print(f"\n📝 Обрабатываю {len(all_files)} файлов...")

    total_lines = 0
    processed_files = 0
    error_files = []

    # Записываем всё в выходной файл
    with open(output_file, "w", encoding="utf-8") as out:
        # Красивый заголовок
        out.write("=" * 80 + "\n")
        out.write(f"📦 СБОРКА КОДА ПРОЕКТА: {project_name}\n")
        out.write("=" * 80 + "\n")
        out.write(f"📅 Дата создания: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        out.write(f"📁 Исходная папка: {project_path}\n")
        out.write(f"📊 Всего файлов: {len(all_files)}\n")
        out.write(f"⏭️  Пропущено: {skipped_count}\n")
        out.write("=" * 80 + "\n\n")

        # Оглавление
        out.write("📑 СОДЕРЖАНИЕ (СПИСОК ВСЕХ ФАЙЛОВ)\n")
        out.write("-" * 80 + "\n")

        for i, f in enumerate(all_files, 1):
            try:
                rel_path = f.relative_to(project_path)
                size_kb = f.stat().st_size / 1024
                out.write(f"{i:4d}. {rel_path} ({size_kb:.1f} KB)\n")
            except:
                pass

        out.write("\n" + "=" * 80 + "\n")
        out.write("📄 ИСХОДНЫЙ КОД ФАЙЛОВ\n")
        out.write("=" * 80 + "\n")

        # Записываем содержимое каждого файла
        for f in all_files:
            try:
                rel_path = f.relative_to(project_path)

                # Пытаемся прочитать файл
                try:
                    with open(f, "r", encoding="utf-8") as inf:
                        content = inf.read()
                except UnicodeDecodeError:
                    # Пробуем другие кодировки
                    try:
                        with open(f, "r", encoding="latin-1") as inf:
                            content = inf.read()
                    except:
                        with open(f, "r", encoding="cp1251") as inf:
                            content = inf.read()

                # Пропускаем полностью пустые файлы
                if not content.strip():
                    skipped_count += 1
                    continue

                lines_count = len(content.splitlines())

                # Красивый разделитель с эмодзи
                out.write("\n\n")
                out.write("🟢 " + "=" * 76 + "\n")
                out.write(f"📍 ПУТЬ: {rel_path}\n")
                out.write(f"📄 ФАЙЛ: {f.name}\n")
                out.write(
                    f"📏 СТРОК: {lines_count} | 💾 РАЗМЕР: {f.stat().st_size / 1024:.1f} KB\n"
                )
                out.write("=" * 80 + "\n\n")

                # Записываем содержимое
                out.write(content)

                # Добавляем перенос строки в конце если его нет
                if not content.endswith("\n"):
                    out.write("\n")

                total_lines += lines_count
                processed_files += 1

                # Прогресс
                if processed_files % 10 == 0:
                    print(f"  ✅ Обработано {processed_files}/{len(all_files)}...")

            except Exception as e:
                error_files.append((rel_path, str(e)))
                out.write(f"\n\n🔴 ОШИБКА ЧТЕНИЯ ФАЙЛА: {rel_path}\n")
                out.write(f"Причина: {e}\n")
                skipped_count += 1

    # Финальная статистика
    output_size = output_file.stat().st_size

    print("\n" + "=" * 60)
    print("📊 СТАТИСТИКА СБОРКИ")
    print("=" * 60)
    print(f"✅ Успешно обработано: {processed_files} файлов")
    print(f"⏭️  Пропущено: {skipped_count} файлов")
    print(f"📝 Всего строк кода: {total_lines:,}")
    print(
        f"💾 Размер отчёта: {output_size / 1024:.1f} KB ({output_size / 1024 / 1024:.2f} MB)"
    )

    if error_files:
        print(f"\n⚠️  Ошибки чтения ({len(error_files)}):")
        for fname, err in error_files[:3]:
            print(f"   • {fname}: {err}")
        if len(error_files) > 3:
            print(f"   ... и ещё {len(error_files) - 3}")

    print(f"\n📁 Файл сохранён: {output_file}")
    print("✅ Готово! Файл можно использовать для анализа.\n")

    return output_file


if __name__ == "__main__":
    try:
        output = collect_all_code()
        print(f"👉 Открой файл: {output.name}")
    except KeyboardInterrupt:
        print("\n\n⚠️  Сборка прервана пользователем.")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback

        traceback.print_exc()
