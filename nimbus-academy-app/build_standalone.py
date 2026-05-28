#!/usr/bin/env python3
"""Build single-file offline HTML — download and open in any browser."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> None:
    subprocess.run([sys.executable, str(ROOT / "build_content.py")], check=True)

    css = read(ROOT / "css" / "app.css") + "\n" + read(ROOT / "css" / "katex.min.css")
    marked = read(ROOT / "js" / "marked.min.js")
    katex = read(ROOT / "js" / "katex.min.js")
    auto_render = read(ROOT / "js" / "auto-render.min.js")
    content = read(ROOT / "js" / "content-bundle.js")
    app = read(ROOT / "js" / "app.js")

    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta name="theme-color" content="#080b16">
  <title>Nimbus Academy · offline</title>
  <style>{css}</style>
</head>
<body>
  <div id="app">
    <aside id="sidebar" class="sidebar" aria-label="Навигация">
      <header class="sidebar-header">
        <div class="logo">
          <span class="logo-mark" aria-hidden="true">◈</span>
          <div>
            <strong>Nimbus Academy</strong>
            <span class="logo-sub">Level 1 · один файл</span>
          </div>
        </div>
        <button type="button" id="sidebar-close" class="icon-btn sidebar-close" aria-label="Закрыть меню">✕</button>
      </header>
      <nav id="doc-list" class="doc-list"></nav>
      <footer class="sidebar-footer">
        <span id="online-status" class="status-pill offline">Offline OK</span>
      </footer>
    </aside>
    <div class="main-shell">
      <header class="topbar">
        <button type="button" id="sidebar-open" class="icon-btn" aria-label="Открыть меню">☰</button>
        <div class="topbar-title">
          <h1 id="page-title">Nimbus Academy</h1>
          <p id="page-subtitle">Выберите документ</p>
        </div>
        <button type="button" id="theme-toggle" class="icon-btn" aria-label="Сменить тему">◐</button>
      </header>
      <main id="content" class="content">
        <section class="welcome-card">
          <h2>Офлайн-версия</h2>
          <p>Один HTML-файл — всё внутри. Откройте в Chrome / Safari на телефоне или компьютере <strong>без интернета</strong>.</p>
          <ul class="welcome-list">
            <li>Логические задания L1 (10 тем)</li>
            <li>Интегрированные задания L1 (pipeline)</li>
          </ul>
        </section>
      </main>
    </div>
  </div>
  <div id="overlay" class="overlay" hidden></div>
  <script>{marked}</script>
  <script>{katex}</script>
  <script>{auto_render}</script>
  <script>{content}</script>
  <script>{app}</script>
</body>
</html>
"""

    out = ROOT / "nimbus-academy-offline.html"
    out.write_text(html, encoding="utf-8")
    size_kb = out.stat().st_size // 1024
    print(f"Wrote {out} ({size_kb} KB)")


if __name__ == "__main__":
    main()
