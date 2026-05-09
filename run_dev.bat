@echo off
echo === COR Engine Development Server ===
echo.
echo Starting Daphne (WebSocket) on port 8000...
start "COR-WebSocket" cmd /k "cd /d %~dp0 && cor_venv\Scripts\activate && python -m daphne cor.asgi:application -p 8000"
echo Starting Django (HTTP + Static) on port 8001...
start "COR-HTTP" cmd /k "cd /d %~dp0 && cor_venv\Scripts\activate && python manage.py runserver 8001"
echo.
echo === Both servers started! ===
echo Daphne WebSocket: ws://127.0.0.1:8000
echo Django HTTP:      http://127.0.0.1:8001/editor/
echo.
echo Close this window to stop both servers.
pause