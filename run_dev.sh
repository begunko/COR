#!/bin/bash
echo "=== COR Engine Development Server ==="
echo "Starting Daphne (WebSocket) on port 8000..."
python -m daphne cor.asgi:application -p 8000 &
echo "Starting Django (HTTP + Static) on port 8001..."
python manage.py runserver 8001 &
echo "=== Both servers started! ==="
echo "Open: http://127.0.0.1:8001/editor/"
wait