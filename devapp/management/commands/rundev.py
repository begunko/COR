import subprocess
import sys
import os
import signal
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Запускает Daphne (ASGI) и Django runserver одновременно для разработки"

    def add_arguments(self, parser):
        parser.add_argument(
            "--daphne-port",
            default=3000,
            type=int,
            help="Порт для Daphne (по умолчанию 3000)",
        )
        parser.add_argument(
            "--django-port",
            default=3001,
            type=int,
            help="Порт для Django runserver (по умолчанию 3001)",
        )

    def handle(self, *args, **options):
        daphne_port = options["daphne_port"]
        django_port = options["django_port"]

        self.stdout.write(self.style.SUCCESS("🚀 Запускаю серверы разработки..."))

        processes = []

        # Запускаем Daphne
        daphne_cmd = [
            sys.executable,
            "-m",
            "daphne",
            "cor.asgi:application",
            "-b",
            "0.0.0.0",
            "-p",
            str(daphne_port),
        ]

        self.stdout.write(f"📡 Daphne (ASGI): http://0.0.0.0:{daphne_port}")
        daphne_process = subprocess.Popen(daphne_cmd)
        processes.append(("Daphne", daphne_process))

        # Запускаем Django runserver
        django_cmd = [
            sys.executable,
            "manage.py",
            "runserver",
            f"0.0.0.0:{django_port}",
        ]

        self.stdout.write(f"🌐 Django: http://0.0.0.0:{django_port}")
        django_process = subprocess.Popen(django_cmd)
        processes.append(("Django", django_process))

        self.stdout.write(
            self.style.SUCCESS("✨ Всё запущено! Нажми Ctrl+C для остановки\n")
        )

        # Ждём завершения и обрабатываем Ctrl+C
        try:
            for name, process in processes:
                process.wait()
        except KeyboardInterrupt:
            self.stdout.write("\n🛑 Останавливаю серверы...")
            for name, process in processes:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
            self.stdout.write(self.style.SUCCESS("✅ Серверы остановлены"))
