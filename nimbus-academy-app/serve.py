#!/usr/bin/env python3
"""Local dev server for Nimbus Academy PWA (browser + offline cache)."""

import http.server
import os
import socketserver
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
PORT = int(os.getenv("NIMBUS_APP_PORT", "8080"))


def build() -> None:
    subprocess.run([sys.executable, str(ROOT / "build_content.py")], check=True)


def main() -> None:
    build()
    os.chdir(ROOT)
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        url = f"http://127.0.0.1:{PORT}/index.html"
        print(f"Nimbus Academy → {url}")
        print("Откройте в браузере. После первой загрузки работает офлайн (Service Worker).")
        print("Android: меню браузера → «Добавить на главный экран».")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
