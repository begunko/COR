#!/usr/bin/env python3
"""
Универсальный сборщик кода Django-проекта COR.
Создаёт папку COR_code/ и в ней:
  - COR_all_code.txt — весь бэкенд-код (без фронтенда)
  - COR_all_code_full.txt — весь код включая фронтенд
  - COR_frontend_code.txt — только static + templates
  - COR_имяприложения_code.txt — для каждого приложения и конфигурации отдельно

Можно запускать из любой папки — скрипт сам найдёт корень проекта.
"""

import os
import sys
from pathlib import Path
from datetime import datetime


def find_project_root():
    """Ищет корень Django-проекта (где лежит manage.py)"""
    current = Path.cwd()

    # Ищем manage.py вверх по дереву директорий
    for parent in [current] + list(current.parents):
        if (parent / "manage.py").exists():
            return parent

    # Если manage.py не найден, ищем характерные папки Django-проекта
    for parent in [current] + list(current.parents):
        # Проверяем наличие settings.py (характерно для Django)
        settings_candidates = list(parent.rglob("settings.py"))
        for s in settings_candidates:
            if "site-packages" not in str(s) and "dist-packages" not in str(s):
                return s.parent.parent  # Родительская папка для папки с settings.py

    return None


def find_django_apps(project_root):
    """
    Находит все Django-приложения и конфигурационные папки в проекте.
    Возвращает словарь: {имя_папки: тип}
    тип может быть: 'app' (приложение) или 'config' (конфигурация проекта)
    """
    components = {}

    for item in project_root.iterdir():
        if not item.is_dir():
            continue

        # Пропускаем заведомо не-Django папки
        if item.name.startswith(".") or item.name.startswith("_"):
            continue
        if item.name in [
            "static",
            "templates",
            "media",
            "node_modules",
            "venv",
            ".venv",
            "env",
            "COR_code",
            "management",
            "vendor",
            "build",
            "dist",
            "docs",
        ]:
            continue

        # Проверяем, является ли это Django-приложением
        has_models = (item / "models.py").exists() or (item / "models").is_dir()
        has_apps = (item / "apps.py").exists()
        has_admin = (item / "admin.py").exists()
        has_views = (item / "views.py").exists()
        has_urls = (item / "urls.py").exists()

        # Это конфигурационная папка проекта?
        has_settings = (item / "settings.py").exists()
        has_wsgi = (item / "wsgi.py").exists()
        has_asgi = (item / "asgi.py").exists()

        if has_settings or has_wsgi or has_asgi:
            # Это конфигурационная папка проекта
            if has_models or has_views:
                # И приложение и конфигурация в одной папке (бывает)
                components[item.name] = "both"
            else:
                components[item.name] = "config"
        elif has_models or (has_apps and (has_views or has_admin or has_urls)):
            # Это Django-приложение
            components[item.name] = "app"

    return dict(sorted(components.items()))


def collect_code(
    project_root,
    app_name=None,
    output_file="output.txt",
    include_static_templates=False,
    mode="backend",  # "backend", "frontend", "all"
):
    """
    Собирает код проекта.

    Args:
        project_root: путь к корню проекта
        app_name: если указано — собирает только это приложение/папку
        output_file: имя выходного файла
        include_static_templates: если True — собирает static/ и templates/
        mode: "backend" - только бэкенд, "frontend" - только фронтенд, "all" - всё вместе
    """
    project_path = str(project_root)

    # === ИСКЛЮЧАЕМЫЕ ДИРЕКТОРИИ ===
    exclude_dirs = {
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".git",
        "venv",
        "env",
        ".venv",
        "ENV",
        ".pixi",
        "node_modules",
        "staticfiles",
        "migrations",
        ".webassets-cache",
        ".idea",
        ".vscode",
        ".vs",
        "build",
        "dist",
        "eggs",
        "develop-eggs",
        ".eggs",
        "parts",
        "sdist",
        "var",
        "docs/_build",
        "site",
        ".tox",
        ".nox",
        ".hypothesis",
        "management",
        "vendor",
        "media",
        "COR_code",  # Исключаем нашу выходную папку
    }

    # === ИСКЛЮЧАЕМЫЕ ФАЙЛЫ ===
    exclude_files = {
        "collect_code.py",
        "collect_frontend.py",
        ".gitignore",
        ".gitattributes",
        ".gitmodules",
        "LICENSE",
        "LICENSE.txt",
        "LICENSE.md",
        "LICENCE",
        ".DS_Store",
        "Thumbs.db",
        "desktop.ini",
        "*.log",
        "*.sqlite3",
        "*.db",
        "db.sqlite3-journal",
        "*.lock",
        ".installed.cfg",
    }

    # === ИСКЛЮЧАЕМЫЕ РАСШИРЕНИЯ ===
    exclude_extensions = {
        ".pyc",
        ".pyo",
        ".pyd",
        ".sqlite3",
        ".db",
        ".sqlite",
        ".log",
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".svg",
        ".ico",
        ".webp",
        ".tiff",
        ".woff",
        ".woff2",
        ".ttf",
        ".eot",
        ".otf",
        ".min.js",
        ".min.css",
        ".map",
        ".so",
        ".dll",
        ".dylib",
        ".exe",
        ".bin",
        ".zip",
        ".tar",
        ".gz",
        ".pdf",
        ".doc",
        ".docx",
        ".mp3",
        ".wav",
        ".ogg",
        ".mp4",
        ".avi",
        ".mov",
        ".fbx",
        ".glb",
        ".blend",
        ".cache",
        ".tmp",
        ".temp",
    }

    if mode == "frontend":
        # Для фронтенда исключаем Python-файлы
        exclude_extensions.update({".py", ".pyc", ".pyo", ".pyd"})
        # Исключаем админские статические файлы
        exclude_files.add("admin.css")
    elif mode == "backend":
        # Для чистого бэкенда исключаем static и templates
        exclude_dirs.update({"static", "templates"})
    # Для mode == "all" — ничего дополнительно не исключаем

    all_files = []
    skipped_count = 0

    # Определяем директорию для сканирования
    if app_name and mode == "backend":
        scan_dir = project_root / app_name
        if not scan_dir.exists():
            print(f"❌ Папка {app_name} не найдена!")
            return 0, 0, 0
        print(f"🔍 Сканирую папку: {app_name}/")
    elif mode == "frontend":
        scan_dir = project_root
        print(f"🔍 Сканирую static/ и templates/ в проекте...")
    else:
        scan_dir = project_root
        if mode == "all":
            print(f"🔍 Сканирую ВЕСЬ проект (включая фронтенд)...")
        else:
            print(f"🔍 Сканирую бэкенд проекта...")

    # Собираем файлы
    for root, dirs, files in os.walk(scan_dir):
        current_path = Path(root)

        # Вычисляем относительный путь для проверки исключений
        try:
            rel_to_project = current_path.relative_to(project_root)
        except ValueError:
            continue

        # Исключаем нежелательные директории
        dirs_to_remove = []
        for d in dirs:
            if d in exclude_dirs or d.startswith("."):
                dirs_to_remove.append(d)
                print(f"  ⏭️  Пропущена директория: {d}/")

        for d in dirs_to_remove:
            dirs.remove(d)

        # Фильтрация по режиму
        rel_str = str(rel_to_project)

        if mode == "frontend":
            # Только static/ и templates/
            if not (rel_str.startswith("static") or rel_str.startswith("templates")):
                continue
        elif mode == "backend":
            # Исключаем static/ и templates/ (уже добавлены в exclude_dirs,
            # но дополнительная проверка не помешает)
            if rel_str.startswith("static") or rel_str.startswith("templates"):
                continue

        # Обрабатываем файлы
        for file in sorted(files):
            file_path = current_path / file
            file_name_lower = file.lower()
            extension = file_path.suffix.lower()

            # Проверки на исключение
            if file in exclude_files or file_name_lower in exclude_files:
                skipped_count += 1
                continue
            if extension in exclude_extensions:
                skipped_count += 1
                continue
            # Исключаем любые COR_*.txt файлы (результаты предыдущих запусков)
            if file.startswith("COR_") and file.endswith(".txt"):
                skipped_count += 1
                continue

            try:
                size = file_path.stat().st_size
                if size == 0:
                    skipped_count += 1
                    continue
                if size > 5 * 1024 * 1024:
                    print(f"  ⚠️  Пропущен большой файл: {file} ({size // 1024}KB)")
                    skipped_count += 1
                    continue
            except:
                continue

            all_files.append(file_path)

    all_files.sort()

    print(f"📝 Записываю {len(all_files)} файлов в {Path(output_file).name}...")

    total_lines = 0
    processed_files = 0

    with open(output_file, "w", encoding="utf-8") as out:
        # Заголовок
        out.write("=" * 80 + "\n")
        if app_name:
            out.write(f"ПАПКА ПРОЕКТА: {app_name}\n")
        elif mode == "frontend":
            out.write("ПРОЕКТ: COR (Frontend)\n")
        elif mode == "all":
            out.write("ПРОЕКТ: COR (Весь код: бэкенд + фронтенд)\n")
        else:
            out.write("ПРОЕКТ: COR (Бэкенд)\n")
        out.write(
            f"Дата создания отчёта: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )
        out.write(f"Режим сбора: {mode}\n")
        out.write(f"Исключено файлов: {skipped_count}\n")
        out.write("=" * 80 + "\n\n")

        # Оглавление
        out.write("📑 СОДЕРЖАНИЕ\n")
        out.write("-" * 80 + "\n")
        for f in all_files:
            try:
                rel_path = f.relative_to(project_root)
                size_kb = f.stat().st_size / 1024
                out.write(f"  {rel_path} ({size_kb:.1f} KB)\n")
            except:
                pass

        out.write("\n" + "=" * 80 + "\n")
        out.write("📄 ИСХОДНЫЙ КОД\n")
        out.write("=" * 80 + "\n")

        # Содержимое файлов
        for f in all_files:
            try:
                rel_path = f.relative_to(project_root)
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

    return processed_files, total_lines, skipped_count


def main():
    print("=" * 80)
    print("🚀 УНИВЕРСАЛЬНЫЙ СБОРЩИК КОДА ДЛЯ COR")
    print("=" * 80)
    print()

    # Ищем корень проекта
    project_root = find_project_root()

    if not project_root:
        print("❌ Не могу найти Django-проект!")
        print("Убедись, что:")
        print("  1. Ты запускаешь скрипт из папки проекта или его подпапки")
        print("  2. В корне проекта есть manage.py")
        print("\nЛибо укажи путь к проекту вручную:")
        print("  python3 collect_code.py /путь/к/проекту")
        return

    print(f"✅ Найден проект: {project_root}")
    print()

    # Создаём выходную папку
    output_dir = project_root / "COR_code"
    output_dir.mkdir(exist_ok=True)
    print(f"📁 Выходная папка: {output_dir}/")
    print()

    # 1. Собираем весь бэкенд (без фронтенда)
    print("=" * 80)
    print("📦 1/4: Собираю ВЕСЬ БЭКЕНД (без фронтенда)...")
    print("=" * 80)
    all_output = output_dir / "COR_all_code.txt"
    files_count, lines_count, skipped = collect_code(
        project_root,
        output_file=str(all_output),
        mode="backend",
    )
    print(f"\n✅ COR_all_code.txt: {files_count} файлов, {lines_count} строк")
    print(f"📄 {all_output}")
    print()

    # 2. Собираем весь проект (бэкенд + фронтенд)
    print("=" * 80)
    print("📦 2/4: Собираю ВЕСЬ ПРОЕКТ (бэкенд + фронтенд)...")
    print("=" * 80)
    all_full_output = output_dir / "COR_all_code_full.txt"
    files_count_full, lines_count_full, skipped_full = collect_code(
        project_root,
        output_file=str(all_full_output),
        mode="all",
    )
    print(
        f"\n✅ COR_all_code_full.txt: {files_count_full} файлов, {lines_count_full} строк"
    )
    print(f"📄 {all_full_output}")
    print()

    # 3. Собираем только фронтенд
    print("=" * 80)
    print("🎨 3/4: Собираю ФРОНТЕНД...")
    print("=" * 80)
    frontend_output = output_dir / "COR_frontend_code.txt"
    fe_files, fe_lines, fe_skipped = collect_code(
        project_root,
        output_file=str(frontend_output),
        mode="frontend",
    )
    print(f"\n✅ COR_frontend_code.txt: {fe_files} файлов, {fe_lines} строк")
    print(f"📄 {frontend_output}")
    print()

    # 4. Собираем каждую папку отдельно (и приложения, и конфигурацию)
    print("=" * 80)
    print("📱 4/4: Собираю отдельные ПАПКИ ПРОЕКТА...")
    print("=" * 80)

    components = find_django_apps(project_root)
    print(f"Найдено папок проекта: {len(components)}")

    if components:
        print("Папки:")
        for name, comp_type in components.items():
            type_label = {
                "app": "📱 приложение",
                "config": "⚙️  конфигурация",
                "both": "📱⚙️  приложение + конфигурация",
            }.get(comp_type, "📁 папка")
            print(f"  • {name} ({type_label})")
        print()

        for i, (name, comp_type) in enumerate(components.items(), 1):
            print(f"[{i}/{len(components)}] Собираю {name}...")
            app_output = output_dir / f"COR_{name}_code.txt"
            app_files, app_lines, app_skipped = collect_code(
                project_root,
                app_name=name,
                output_file=str(app_output),
                mode="backend",
            )
            type_label = {
                "app": "приложение",
                "config": "конфигурация",
                "both": "приложение+конфигурация",
            }.get(comp_type, "папка")
            print(
                f"  ✅ COR_{name}_code.txt ({type_label}): {app_files} файлов, {app_lines} строк"
            )
            print()

    # Финальная статистика
    print("=" * 80)
    print("🎉 ГОТОВО! Все файлы созданы в папке COR_code/")
    print("=" * 80)
    print(f"📁 {output_dir}")
    print(f"📄 Созданные файлы:")

    total_size = 0
    for f in sorted(output_dir.iterdir()):
        if f.is_file() and f.name.startswith("COR_"):
            size_kb = f.stat().st_size / 1024
            total_size += size_kb
            # Определяем тип файла для красивого вывода
            if "frontend" in f.name:
                icon = "🎨"
            elif "all_code_full" in f.name:
                icon = "📦"
            elif "all_code" in f.name:
                icon = "📦"
            else:
                icon = "📱"
            print(f"  {icon} {f.name} ({size_kb:.1f} KB)")

    print(f"\n💾 Общий размер: {total_size:.1f} KB ({total_size/1024:.2f} MB)")
    print()


if __name__ == "__main__":
    # Можно передать путь к проекту через аргумент командной строки
    if len(sys.argv) > 1:
        custom_path = Path(sys.argv[1])
        if custom_path.exists():
            os.chdir(custom_path)
        else:
            print(f"❌ Указанный путь не существует: {custom_path}")
            sys.exit(1)

    main()
