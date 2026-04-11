"""Start the chess server with automatic tunnel creation."""

import asyncio
import subprocess
import sys
import time
from pathlib import Path

# Add parent directory to path to import server
sys.path.insert(0, str(Path(__file__).parent))

from server import main as server_main, get_public_ip, get_local_ip


def check_localtunnel() -> bool:
    """Check if localtunnel is available."""
    try:
        subprocess.run(["lt", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def start_tunnel(port: int = 8000) -> subprocess.Popen:
    """Start localtunnel in background."""
    print("🌐 Запуск туннеля...")
    process = subprocess.Popen(
        ["lt", "--port", str(port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    time.sleep(4)  # Wait for tunnel to establish
    return process


def extract_tunnel_url(process: subprocess.Popen) -> str:
    """Try to extract tunnel URL from process output."""
    try:
        # Read from stderr (localtunnel outputs URL there)
        time.sleep(1)
        process.poll()
        # Unfortunately, localtunnel doesn't output URL to stdout/stderr easily
        # We'll need to tell user to check the output
        return ""
    except Exception:
        return ""


def main():
    print("=" * 60)
    print("🚀 Запуск сервера шахмат с туннелем")
    print("=" * 60)
    print()
    
    if not check_localtunnel():
        print("❌ Localtunnel не найден!")
        print()
        print("Установите localtunnel:")
        print("  npm install -g local-tunnel")
        print()
        print("Или используйте отдельный скрипт:")
        print("  python tunnel_helper.py")
        print()
        return
    
    # Start tunnel
    tunnel_process = start_tunnel(8000)
    
    print("✅ Туннель запущен!")
    print()
    print("📋 Проверьте вывод выше - там должен быть публичный URL")
    print("   Обычно он выглядит как: https://xxxxx.loca.lt")
    print()
    print("=" * 60)
    print()
    
    # Start server
    try:
        server_main()
    except KeyboardInterrupt:
        print("\n🛑 Остановка сервера и туннеля...")
        tunnel_process.terminate()
        tunnel_process.wait()


if __name__ == "__main__":
    main()
