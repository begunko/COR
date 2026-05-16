# ⬡ COR Engine

## Браузерный 3D-движок для совместного создания миров

<p align="center">
  <img src="https://via.placeholder.com/1200x400/12122a/ff6600?text=COR+Engine" width="100%">
</p>

<p align="center">
  <strong>Редактируй вместе. Создавай без границ.</strong>
</p>

<p align="center">
  <a href="#-демо">Демо</a> •
  <a href="#-возможности">Возможности</a> •
  <a href="#-архитектура">Архитектура</a> •
  <a href="#-api">API</a> •
  <a href="#-лицензия">Лицензия</a>
</p>

Понял, друг! Сейчас сделаю обычный текст, без хитрых форматирований, который можно просто скопировать и вставить. Поехали.

---

# ⬡ COR Engine

Браузерный 3D-движок для совместного создания миров

Редактируй вместе. Создавай без границ.

---

## 🎯 О проекте

COR Engine — это браузерный 3D-движок, созданный для командной работы над игровыми мирами в реальном времени.

В отличие от Unity и Unreal, COR работает прямо в браузере. Ничего не нужно скачивать — открыл ссылку и попал в редактор.

Ключевая фишка: До 1000 человек могут одновременно редактировать один и тот же мир. Как Google Docs, но для 3D-миров.

---

## ✨ Возможности

| Возможность | Статус |
|-------------|--------|
| 🎨 3D-редактор (кубы, сферы, цилиндры) | ✅ |
| 👥 Совместная работа через WebSocket | ✅ |
| 💾 Автосохранение в базу данных | ✅ |
| 🗺 Гексагональные чанки-соты | ✅ |
| 🛠 Панель инструментов с наборами | ✅ |
| 📐 Трансформация объектов | ✅ |
| 🎭 Undo/Redo (Ctrl+Z/Ctrl+Y) | ✅ |
| 🎮 Режим Play (просмотр готового мира) | 🚧 |
| 🤖 AI-генерация ассетов | ✅ |
| 📦 Ассеты из примитивов | ✅ |
| 👤 Ролевая система | 🚧 |

---

## 🏗 Архитектура

```
┌─────────────────────────────────────────────────────────────┐
│                         Браузер                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Babylon.js  │  │  Интерфейс  │  │  WebSocket Client   │  │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘  │
└─────────┼────────────────┼────────────────────┼─────────────┘
          │ HTTP           │ Статика            │ WS
          ▼                ▼                    ▼
┌─────────────────────────────────────────────────────────────┐
│                      Сервер (Django + Daphne)               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Users │ Projects │ Scenes │ Tools │ Assets │ AI    │    │
│  └─────────────────────────────────────────────────────┘    │
│                          │                                  │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                    PostgreSQL                       │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Быстрый старт

### Требования

Python 3.14+
16+ GB RAM (для AI-генерации)
Git
Ollama (опционально, для AI-функций)

### Установка

1. Клонируй репозиторий

git clone https://github.com/begunko/COR.git
cd COR

2. Создай виртуальное окружение

Windows:
python -m venv venv
venv\Scripts\activate

Linux/Mac:
python -m venv venv
source venv/bin/activate

3. Установи зависимости

pip install -r requirements.txt

4. Примени миграции

python manage.py migrate

5. Создай суперпользователя

python manage.py createsuperuser

6. Запусти сервер

python manage.py rundev

Команда rundev запускает сразу два сервера: Daphne (WebSocket) и Django (HTTP)

### После запуска

Редактор: http://localhost:8001/editor/
Админка: http://localhost:8001/admin/
Мониторинг: http://localhost:8001/monitoring/

### Установка AI (Ollama) — опционально

Если хочешь использовать AI-генерацию ассетов:

1. Установи Ollama
curl -fsSL https://ollama.com/install.sh | sh

2. Скачай модель (9 GB, займёт 10-30 минут)
ollama pull qwen2.5:14b

3. Проверь, что работает
ollama run qwen2.5:14b "Привет"

Без AI движок тоже работает, но функции генерации ассетов будут недоступны.

---

## 🎮 Как это работает

### Гексагональные чанки

Мир построен на шестигранных призмах, которые автоматически стыкуются друг с другом. Никаких щелей и ручной подгонки.

# Координаты чанка
grid_q, grid_r = 0, 0  # осевые координаты
grid_y = 0              # вертикальный слой

# 18 соседей
neighbors = chunk.activate_neighbors()

### AI-генерация ассетов

# Создать простой ассет
python ai_create_asset_fixed.py

# Массовая генерация (на ночь)
python ai_mass_asset_generator_advanced.py

Выбери сложность:
1 - Простой (5-12 элементов)
2 - Средний (12-25 элементов)
3 - Сложный (25-50 элементов) - рекомендуется
4 - Эпический (50-100 элементов)
5 - Безумный (100-200 элементов) - ОСТОРОЖНО!

### Совместное редактирование

// WebSocket синхронизация
socket.send({
    type: 'object_updated',
    server_id: objectId,
    position: {x, y, z}
});

---

## 📁 Структура проекта
```
cor-engine/
├── cor/                    # Настройки проекта
│   ├── settings.py
│   ├── consumers.py        # WebSocket
│   └── routing.py
│
├── scenes/                 # Миры, чанки, объекты
├── assets/                 # Ассеты (JSON-объекты)
├── tools/                  # Инструменты и наборы
├── users/                  # Пользователи и права
├── monitoring/             # Системный мониторинг
│
├── static/                 # Фронтенд
│   ├── css/               # Стили
│   └── js/                # JavaScript (Babylon.js)
│
├── templates/              # HTML-шаблоны
│
├── ai_*.py                 # Скрипты AI-генерации
└── requirements.txt
```
---

## 🛠 API

GET  /api/v1/assets/              - Список ассетов
GET  /api/v1/assets/{id}/         - Детали ассета
POST /api/v1/assets/{id}/         - Обновление ассета
GET  /api/v1/tools/{id}/          - Детали инструмента
POST /api/v1/tools/{id}/          - Обновление инструмента
GET  /api/v1/toolbar/             - Наборы инструментов
GET  /api/chunk/{id}/load/        - Загрузка чанка
POST /api/chunk/{id}/save/        - Сохранение чанка
GET  /api/monitoring/             - Статистика системы

### WebSocket

ws://host:8000/ws/chunk/{chunk_id}/
ws://host:8000/ws/asset/{asset_id}/

---

## 🐛 Известные проблемы и решения

Проблема: Ошибка 500 при загрузке чанка
Решение: Убедись, что в properties правильная структура (geometry и material должны быть словарями)

Проблема: AI долго думает (40+ минут)
Решение: Используй уровень сложности "Сложный" (3), а не "Безумный" (5)

Проблема: Объекты не отображаются
Решение: Проверь координаты (должны быть в пределах ±25 от центра чанка)

Проблема: WebSocket не подключается
Решение: Убедись, что Daphne запущен на порту 8000

---

## 🔧 Полезные команды

# Запуск сервера (HTTP + WebSocket)
python manage.py rundev

# Проверка объектов в чанке
python check_chunk.py <chunk_id>

# Генерация ассета через AI
python ai_create_asset_fixed.py

# Массовая генерация ассетов
python ai_mass_asset_generator_advanced.py

# Заполнение чанка объектами
python ai_fill_chunk.py <chunk_id>

# Создание бэкапа базы данных
python manage.py dumpdata > backup.json

# Восстановление из бэкапа
python manage.py loaddata backup.json

---

## 🤝 Как помочь проекту

Поставь звёздочку на GitHub
Сообщи о багах в Issues
Сделай Pull Request с новыми фичами
Поддержи проект на Boosty или GitHub Sponsors

---

## 📄 Лицензия

MIT License — свободно используйте, модифицируйте, распространяйте.

Copyright (c) 2026 COR Engine Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...

---

## 🌟 Контакты

Telegram: @begunko
Email: begunko@gmail.com.com
GitHub: https://github.com/begunko/COR

---

Сделано с ❤️ для инди-разработчиков по всему миру

⬡ COR Engine — твой мир начинается здесь. 🚀

---
