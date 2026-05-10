#!/usr/bin/env python3
"""
Скрипт для сбора кода проекта COR в один текстовый файл.
Исключает автоматически генерируемые файлы, миграции, кэш, базы данных,
сам скрипт сбора, служебные файлы Git и лицензии.
"""

import os
from pathlib import Path
from datetime import datetime


def collect_project_code(project_path=".", output_file="COR_project_code.txt"):
    """Собирает содержимое всех файлов с кодом в один текстовый файл"""

    # === ИСКЛЮЧАЕМЫЕ ДИРЕКТОРИИ ===
    exclude_dirs = {
        # Python
        "__pycache__",  # Кэш Python
        ".pytest_cache",  # Кэш тестов pytest
        ".mypy_cache",  # Кэш mypy
        ".ruff_cache",  # Кэш Ruff линтера
        # Git (служебная)
        ".git",  # Вся папка .git
        # Виртуальные окружения
        "venv",
        "env",
        ".venv",
        "ENV",
        ".pixi",  # Pixi package manager
        # Зависимости
        "node_modules",  # Node.js
        # Django
        "staticfiles",  # Собранная статика
        "migrations",  # Автоматические миграции
        ".webassets-cache",  # Кэш Flask/Django ассетов
        # IDE
        ".idea",
        ".vscode",
        ".vs",
        ".spyproject",
        ".spyderproject",
        ".ropeproject",  # Rope refactoring
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
        ".nox",  # Тестовые окружения
        ".hypothesis",  # Hypothesis тесты
        "vendor"
    }

    # === ИСКЛЮЧАЕМЫЕ ФАЙЛЫ (по имени, не по расширению) ===
    exclude_files = {
        # Этот скрипт
        "collect_code.py",
        # Git
        ".gitignore",  # Служебный файл Git
        ".gitattributes",  # Настройки Git атрибутов
        ".gitmodules",  # Подмодули Git
        # Лицензии (полные тексты неинформативны для анализа кода)
        "LICENSE",
        "LICENSE.txt",
        "LICENSE.md",
        "LICENCE",  # Альтернативное написание
        # Разное
        ".DS_Store",  # macOS
        "Thumbs.db",  # Windows
        "desktop.ini",  # Windows
        # Резервные копии
        "global_packages_backup.txt",  # Твой бэкап пакетов
        # Логи
        "*.log",  # Все логи
        "pip-log.txt",
        # Базы данных
        "*.sqlite3",
        "*.db",
        "db.sqlite3-journal",
        # Блокировки и кэш
        "*.lock",  # Файлы блокировки (package-lock.json и т.д., если не нужны)
        ".installed.cfg",
        # ENV примеры (обычно шаблонные)
        ".env.example",  # Раскомментируй, если хочешь исключить
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
        # Логи
        ".log",
        # Изображения (бинарные)
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".svg",
        ".ico",
        ".webp",
        ".tiff",
        # Шрифты (бинарные)
        ".woff",
        ".woff2",
        ".ttf",
        ".eot",
        ".otf",
        # Минифицированные (нечитаемые)
        ".min.js",
        ".min.css",
        # Source maps (не нужны для анализа)
        ".map",
        # Скомпилированные/бинарные
        ".so",
        ".dll",
        ".dylib",  # Библиотеки
        ".exe",
        ".bin",  # Исполняемые
        ".zip",
        ".tar",
        ".gz",  # Архивы
        ".pdf",
        ".doc",
        ".docx",  # Документы
        # Аудио/видео
        ".mp3",
        ".wav",
        ".ogg",
        ".mp4",
        ".avi",
        ".mov",
        # 3D модели (бинарные)
        ".fbx",
        ".glb",
        ".blend",
        # Кэш и временные
        ".cache",
        ".tmp",
        ".temp",
    }

    all_files = []
    skipped_count = 0
    skipped_files_list = []

    print("🔍 Сканирую файлы проекта...")

    # Собираем список файлов
    for root, dirs, files in os.walk(project_path):
        current_path = Path(root)

        # Исключаем нежелательные директории
        dirs_to_remove = []
        for d in dirs:
            if d in exclude_dirs or d.startswith("."):
                dirs_to_remove.append(d)

        for d in dirs_to_remove:
            dirs.remove(d)
            print(f"  ⏭️  Пропущена директория: {d}/")

        # Обрабатываем файлы в текущей директории
        for file in sorted(files):
            file_path = current_path / file
            file_name_lower = file.lower()
            extension = file_path.suffix.lower()

            # Проверка: исключаем по имени файла
            if file in exclude_files or file_name_lower in exclude_files:
                skipped_count += 1
                skipped_files_list.append(f"{file} (по имени)")
                continue

            # Проверка: исключаем по расширению
            if extension in exclude_extensions:
                skipped_count += 1
                skipped_files_list.append(f"{file} (расширение {extension})")
                continue

            # Проверка: исключаем сам выходной файл (чтобы не собирать предыдущие результаты)
            if file == output_file:
                skipped_count += 1
                skipped_files_list.append(f"{file} (выходной файл)")
                continue

            # Проверка размера файла
            try:
                size = file_path.stat().st_size
                if size == 0:
                    skipped_count += 1
                    skipped_files_list.append(f"{file} (пустой)")
                    continue
                if size > 5 * 1024 * 1024:  # > 5MB
                    print(f"  ⚠️  Пропущен большой файл: {file} ({size // 1024}KB)")
                    skipped_count += 1
                    continue
            except:
                continue

            all_files.append(file_path)

    # Сортируем для красивого вывода
    all_files.sort()

    if skipped_files_list:
        print(f"\n📋 Пропущенные файлы ({len(skipped_files_list)}):")
        for sf in skipped_files_list[:10]:  # Показываем первые 10
            print(f"   • {sf}")
        if len(skipped_files_list) > 10:
            print(f"   ... и ещё {len(skipped_files_list) - 10}")

    print(f"\n📝 Записываю {len(all_files)} файлов в {output_file}...")

    total_lines = 0
    processed_files = 0

    with open(output_file, "w", encoding="utf-8") as out:
        # Заголовок файла
        out.write("=" * 80 + "\n")
        out.write("ПРОЕКТ: COR\n")
        out.write(
            f"Дата создания отчёта: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )
        out.write(f"Исключено файлов: {skipped_count}\n")
        out.write("=" * 80 + "\n\n")

        # Оглавление (список всех файлов)
        out.write("📑 СОДЕРЖАНИЕ (ФАЙЛЫ ПРОЕКТА)\n")
        out.write("-" * 80 + "\n")

        for f in all_files:
            try:
                rel_path = f.relative_to(project_path)
                size_kb = f.stat().st_size / 1024
                out.write(f"  {rel_path} ({size_kb:.1f} KB)\n")
            except:
                pass

        out.write("\n" + "=" * 80 + "\n")
        out.write("📄 ИСХОДНЫЙ КОД ФАЙЛОВ\n")
        out.write("=" * 80 + "\n")

        # Записываем содержимое каждого файла
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
                print(f"  ✅ Обработан: {rel_path}")

            except UnicodeDecodeError:
                print(f"  ⚠️  Пропущен бинарный файл: {f.name}")
                skipped_count += 1
            except Exception as e:
                print(f"  ❌ Ошибка при чтении {f.name}: {e}")
                out.write(f"\n\n🔴 ФАЙЛ: {rel_path}\n")
                out.write(f"[ОШИБКА ЧТЕНИЯ: {e}]\n")

    # Финальная статистика
    print("\n" + "=" * 80)
    print("📊 СТАТИСТИКА СБОРА КОДА")
    print("=" * 80)
    print(f"✅ Успешно обработано файлов: {processed_files}")
    print(f"⏭️  Пропущено файлов: {skipped_count}")
    print(f"📝 Всего строк кода: {total_lines}")
    print(f"💾 Размер отчёта: {Path(output_file).stat().st_size / 1024:.1f} KB")
    print(f"📁 Отчёт сохранён в: {output_file}")
    print("\nГотово! Можешь отправить мне этот файл для анализа.")


if __name__ == "__main__":
    if Path("manage.py").exists():
        print("🚀 Начинаю сбор кода проекта из корневой директории...\n")
        collect_project_code()
    else:
        print(
            "❌ Ошибка: скрипт должен быть запущен из корневой директории проекта (рядом с manage.py)"
        )
        print("Перейди в директорию проекта и запусти заново.")
