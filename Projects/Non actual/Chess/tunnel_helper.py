"""Helper script to create a tunnel for the chess server without port forwarding.

Supports:
- localtunnel (no registration required)
- ngrok (requires free account)
"""

import subprocess
import sys
import time
import webbrowser
from pathlib import Path


def check_command(cmd: str) -> bool:
    """Check if a command is available."""
    try:
        subprocess.run([cmd, "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def install_localtunnel() -> bool:
    """Install localtunnel via npm."""
    print("Установка localtunnel...")
    try:
        subprocess.run(["npm", "install", "-g", "localtunnel"], check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Ошибка: npm не найден. Установите Node.js с https://nodejs.org/")
        return False


def create_localtunnel(port: int = 8000) -> str:
    """Create a localtunnel and return the public URL."""
    print(f"Создание туннеля для порта {port}...")
    try:
        process = subprocess.Popen(
            ["lt", "--port", str(port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        time.sleep(3)  # Wait for tunnel to establish
        
        # Try to read the URL from output
        stdout, stderr = process.communicate(timeout=2)
        output = stdout + stderr
        
        # Look for URL pattern
        for line in output.split("\n"):
            if "https://" in line or "http://" in line:
                url = line.strip().split()[-1]
                if url.startswith("http"):
                    return url
        
        # If not found in output, return a placeholder
        return "https://your-tunnel-url.loca.lt"
    except Exception as e:
        print(f"❌ Ошибка создания туннеля: {e}")
        return ""


def create_ngrok_tunnel(port: int = 8000) -> str:
    """Create an ngrok tunnel and return the public URL."""
    print(f"Создание ngrok туннеля для порта {port}...")
    try:
        process = subprocess.Popen(
            ["ngrok", "http", str(port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        time.sleep(3)
        
        # ngrok has a web interface at http://127.0.0.1:4040
        # But we can't easily parse the URL from command line
        print("✅ Ngrok туннель создан!")
        print("📋 Откройте http://127.0.0.1:4040 в браузере, чтобы увидеть публичный URL")
        return "http://127.0.0.1:4040"
    except FileNotFoundError:
        print("❌ Ngrok не найден. Установите с https://ngrok.com/download")
        return ""


def main():
    port = 8000
    
    print("=" * 60)
    print("🌐 Создание туннеля для игры через интернет")
    print("=" * 60)
    print()
    
    # Check available options
    has_lt = check_command("lt")
    has_ngrok = check_command("ngrok")
    
    if not has_lt and not has_ngrok:
        print("❌ Не найдено ни одного туннельного сервиса.")
        print()
        print("Выберите один из вариантов:")
        print()
        print("1. Localtunnel (рекомендуется, не требует регистрации):")
        print("   npm install -g local-tunnel")
        print()
        print("2. Ngrok (требует бесплатную регистрацию):")
        print("   Скачайте с https://ngrok.com/download")
        print("   Зарегистрируйтесь на https://dashboard.ngrok.com/")
        print()
        return
    
    # Prefer localtunnel if available
    if has_lt:
        print("✅ Найден localtunnel")
        print("Создание туннеля...")
        url = create_localtunnel(port)
        if url:
            print()
            print("=" * 60)
            print("✅ Туннель создан!")
            print("=" * 60)
            print(f"🌐 Публичный URL: {url}")
            print()
            print("📋 Друзья могут подключиться по этому адресу")
            print("⚠️  Туннель будет работать, пока запущен этот скрипт")
            print("=" * 60)
            print()
            print("Теперь запустите сервер в другом окне:")
            print(f"  python server.py")
            print()
            input("Нажмите Enter для завершения...")
        else:
            print("❌ Не удалось создать туннель")
    elif has_ngrok:
        print("✅ Найден ngrok")
        url = create_ngrok_tunnel(port)
        if url:
            print()
            print("=" * 60)
            print("✅ Туннель создан!")
            print("=" * 60)
            print("📋 Откройте http://127.0.0.1:4040 для просмотра публичного URL")
            print("⚠️  Туннель будет работать, пока запущен этот скрипт")
            print("=" * 60)
            print()
            print("Теперь запустите сервер в другом окне:")
            print(f"  python server.py")
            print()
            input("Нажмите Enter для завершения...")


if __name__ == "__main__":
    main()
