#!/usr/bin/env python3
"""Build standalone nimbus-bci-problems.html from problems data."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "nimbus-bci-problems.html"


def fix(text: str) -> str:
    if not text:
        return text
    try:
        return text.encode("cp1251").decode("utf-8")
    except (UnicodeDecodeError, UnicodeEncodeError):
        return text


# Source: Nimbus BCI Problems React component (strings cp1251-mojibake fixed)
RAW = r'''
id: "EEG", title: "TITLE1", level: 1, tag: "TAG1", color: "#00e5ff", emoji: "⚡", difficulty: "DIFF1",
description: `DESC1`,
solution: `SOL1`,
'''

# Full problems embedded as JSON-like structure after fix - load from external js export
PROBLEMS_JS = Path(__file__).with_name("problems-data.js")


def load_problems_from_user_js(path: Path) -> list:
    text = path.read_text(encoding="utf-8")
    # Strip imports and exports
    start = text.find("const problems = [")
    if start < 0:
        raise ValueError("problems array not found")
    end = text.find("];", start)
    block = text[start + len("const problems = ") : end + 1]
    # Convert JS to JSON-ish: backticks to quotes, fix keys
    block = re.sub(r"(\w+):", r'"\1":', block)
    block = block.replace("`", '"')
    block = re.sub(r",\s*}", "}", block)
    block = re.sub(r",\s*]", "]", block)
    # Remove comments
    block = re.sub(r"//[^\n]*", "", block)
    try:
        return json.loads(block)
    except json.JSONDecodeError:
        return None


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Nimbus BCI Problems</title>
  <style>
    * {{ box-sizing: border-box; }}
    html, body {{ height: 100%; margin: 0; }}
    body {{
      min-height: 100vh;
      background: #010409;
      color: #e6edf3;
      font-family: Inter, "Segoe UI", system-ui, sans-serif;
      display: flex;
      flex-direction: column;
    }}
    .header {{
      background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
      border-bottom: 1px solid #21262d;
      padding: 20px 24px;
      display: flex;
      align-items: center;
      gap: 16px;
      position: sticky;
      top: 0;
      z-index: 100;
    }}
    .logo {{
      width: 36px; height: 36px;
      background: linear-gradient(135deg, #00e5ff, #7c4dff);
      border-radius: 10px;
      display: grid; place-items: center;
      font-size: 18px; flex-shrink: 0;
    }}
    .header-title {{ font-size: 16px; font-weight: 700; }}
    .header-sub {{ font-size: 11px; color: #8b949e; margin-top: 1px; }}
    .level-dots {{ margin-left: auto; display: flex; gap: 8px; }}
    .dot {{ width: 8px; height: 8px; border-radius: 50%; background: #21262d; }}
    .dot.done {{ background: #00c853; }}
    .layout {{ display: flex; flex: 1; min-height: 0; }}
    .sidebar {{
      width: 300px; border-right: 1px solid #21262d;
      overflow-y: auto; background: #0d1117; flex-shrink: 0;
    }}
    .level-head {{
      padding: 10px 16px 6px; font-size: 10px; color: #8b949e;
      font-weight: 700; letter-spacing: 1px; text-transform: uppercase;
      border-bottom: 1px solid #21262d; background: #010409;
      position: sticky; top: 0;
    }}
    .level-badge {{
      background: #21262d; color: #e6edf3; padding: 2px 6px;
      border-radius: 4px; margin-right: 6px; font-size: 9px;
    }}
    .prob-item {{
      padding: 12px 16px; cursor: pointer;
      border-bottom: 1px solid #161b22;
      border-left: 3px solid transparent;
      transition: background 0.15s;
    }}
    .prob-item:hover {{ background: #161b22; }}
    .prob-item.active {{ background: #161b22; }}
    .prob-row {{ display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }}
    .prob-title {{ font-size: 12px; font-weight: 600; color: #c9d1d9; flex: 1; }}
    .prob-item.active .prob-title {{ color: #e6edf3; }}
    .prob-meta {{ display: flex; gap: 6px; align-items: center; flex-wrap: wrap; }}
    .tag {{
      font-size: 9px; padding: 1px 6px; border-radius: 3px; font-weight: 600;
    }}
    .main {{ flex: 1; overflow-y: auto; }}
    .empty {{
      display: flex; flex-direction: column; align-items: center;
      justify-content: center; min-height: 60vh; color: #8b949e; gap: 16px; padding: 24px;
    }}
    .empty h2 {{ font-size: 18px; font-weight: 600; color: #c9d1d9; margin: 0; }}
    .empty p {{ font-size: 13px; max-width: 400px; text-align: center; line-height: 1.6; margin: 0; }}
    .tags-row {{ display: flex; gap: 12px; flex-wrap: wrap; justify-content: center; max-width: 500px; }}
    .prob-header {{ padding: 24px; border-bottom: 1px solid #21262d; background: #0d1117; }}
    .prob-header-inner {{ display: flex; align-items: flex-start; gap: 16px; }}
    .prob-icon {{
      width: 48px; height: 48px; flex-shrink: 0; border-radius: 12px;
      display: grid; place-items: center; font-size: 22px;
    }}
    .prob-badges {{ display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }}
    .badge {{
      font-size: 10px; padding: 2px 8px; border-radius: 4px;
      background: #21262d; color: #8b949e; font-family: ui-monospace, monospace;
    }}
    .prob-h2 {{ font-size: 20px; font-weight: 700; margin: 8px 0 0; }}
    .btn-solved {{
      padding: 8px 16px; border-radius: 8px; cursor: pointer;
      font-size: 12px; font-weight: 600; flex-shrink: 0;
      background: #21262d; border: 1px solid #30363d; color: #8b949e;
    }}
    .btn-solved.done {{ background: #00c85330; border-color: #00c853; color: #00c853; }}
    .tabs {{ display: flex; border-bottom: 1px solid #21262d; background: #0d1117; padding: 0 24px; }}
    .tab {{
      padding: 12px 20px; background: transparent; border: none;
      border-bottom: 2px solid transparent; color: #8b949e;
      cursor: pointer; font-size: 13px;
    }}
    .tab.active {{ color: #e6edf3; font-weight: 600; }}
    .content {{ padding: 24px; max-width: 860px; }}
    .content h3 {{ color: #e6edf3; font-size: 15px; font-weight: 700; margin: 16px 0 8px; }}
    .content h4 {{ color: #8b949e; font-size: 13px; font-weight: 600; margin: 12px 0 4px; text-transform: uppercase; letter-spacing: 0.5px; }}
    .content p {{ color: #c9d1d9; font-size: 13px; line-height: 1.7; margin: 4px 0; }}
    .content li {{ color: #c9d1d9; font-size: 13px; line-height: 1.7; margin-left: 16px; }}
    .content code {{
      background: #161b22; border: 1px solid #30363d; border-radius: 4px;
      padding: 1px 5px; color: #79c0ff; font-size: 12px;
    }}
    pre {{
      background: #0d1117; border: 1px solid #30363d; border-radius: 8px;
      padding: 16px; overflow-x: auto; font-size: 12px; line-height: 1.6;
      color: #e6edf3; margin: 12px 0;
      font-family: ui-monospace, "JetBrains Mono", monospace;
    }}
    .table-line {{ color: #8b949e; font-size: 12px; font-family: monospace; line-height: 1.8; }}
    @media (max-width: 768px) {{
      .layout {{ flex-direction: column; }}
      .sidebar {{ width: 100%; max-height: 40vh; border-right: 0; border-bottom: 1px solid #21262d; }}
    }}
  </style>
</head>
<body>
  <header class="header">
    <div class="logo">🧠</div>
    <div>
      <div class="header-title">Nimbus BCI Problems</div>
      <div class="header-sub" id="subtitle"></div>
    </div>
    <div class="level-dots" id="level-dots"></div>
  </header>
  <div class="layout">
    <aside class="sidebar" id="sidebar"></aside>
    <main class="main" id="main"></main>
  </div>
  <script>
    const PROBLEMS = __PROBLEMS_JSON__;
    const LEVEL_NAMES = __LEVEL_NAMES_JSON__;
    const TAG_COLORS = __TAG_COLORS_JSON__;

    let selectedId = null;
    let tab = "problem";
    const solved = JSON.parse(localStorage.getItem("nimbus-bci-solved") || "{{}}");

    function saveSolved() {{
      localStorage.setItem("nimbus-bci-solved", JSON.stringify(solved));
    }}

    function renderContent(text) {{
      const parts = text.split(/(```[\\s\\S]*?```)/g);
      const frag = document.createDocumentFragment();
      parts.forEach(part => {{
        if (part.startsWith("```")) {{
          const pre = document.createElement("pre");
          pre.textContent = part.replace(/^```\\w*\\n?/, "").replace(/```$/, "");
          frag.appendChild(pre);
          return;
        }}
        part.split("\\n").forEach(line => {{
          if (line.startsWith("## ")) {{
            const h = document.createElement("h3");
            h.textContent = line.slice(3);
            frag.appendChild(h);
          }} else if (line.startsWith("### ")) {{
            const h = document.createElement("h4");
            h.textContent = line.slice(4);
            frag.appendChild(h);
          }} else if (line.startsWith("- ")) {{
            const li = document.createElement("li");
            li.textContent = line.slice(2);
            frag.appendChild(li);
          }} else if (line.startsWith("| ")) {{
            const d = document.createElement("div");
            d.className = "table-line";
            d.textContent = line;
            frag.appendChild(d);
          }} else if (line.trim() === "") {{
            frag.appendChild(document.createElement("br"));
          }} else {{
            const p = document.createElement("p");
            p.innerHTML = line
              .replace(/\\*\\*(.+?)\\*\\*/g, "<strong style=\\"color:#e6edf3\\">$1</strong>")
              .replace(/`([^`]+)`/g, '<code>$1</code>');
            frag.appendChild(p);
          }}
        }});
      }});
      return frag;
    }}

    function renderDots() {{
      const el = document.getElementById("level-dots");
      el.innerHTML = "";
      for (let l = 1; l <= 9; l++) {{
        const all = PROBLEMS.filter(p => p.level === l);
        const done = all.every(p => solved[p.id]);
        const d = document.createElement("div");
        d.className = "dot" + (done && all.length ? " done" : "");
        d.title = "Уровень " + l;
        el.appendChild(d);
      }}
    }}

    function renderSidebar() {{
      const el = document.getElementById("sidebar");
      el.innerHTML = "";
      const levels = [...new Set(PROBLEMS.map(p => p.level))].sort((a,b) => a-b);
      levels.forEach(level => {{
        const head = document.createElement("div");
        head.className = "level-head";
        head.innerHTML = '<span class="level-badge">Ур.' + level + '</span>' + (LEVEL_NAMES[level] || "");
        el.appendChild(head);
        PROBLEMS.filter(p => p.level === level).forEach(p => {{
          const item = document.createElement("div");
          item.className = "prob-item" + (selectedId === p.id ? " active" : "");
          item.style.borderLeftColor = selectedId === p.id ? p.color : "transparent";
          item.innerHTML =
            '<div class="prob-row"><span>' + p.emoji + '</span>' +
            '<span class="prob-title">' + p.title + '</span>' +
            (solved[p.id] ? '<span style="color:#00c853">✓</span>' : '') +
            '</div><div class="prob-meta">' +
            '<span class="tag" style="color:' + p.color + ';background:' + p.color + '18;border:1px solid ' + p.color + '40">' + p.tag + '</span>' +
            '<span style="font-size:9px;color:#8b949e">' + p.difficulty + '</span>' +
            '<span style="font-size:9px;color:#8b949e;background:#21262d;padding:1px 5px;border-radius:3px;margin-left:auto">' + p.id + '</span>' +
            '</div>';
          item.onclick = () => {{ selectedId = p.id; tab = "problem"; render(); }};
          el.appendChild(item);
        }});
      }});
    }}

    function renderMain() {{
      const el = document.getElementById("main");
      const prob = PROBLEMS.find(p => p.id === selectedId);
      if (!prob) {{
        el.innerHTML = '<div class="empty"><div style="font-size:48px">🧠</div>' +
          '<h2>Выбери задачу из списка</h2>' +
          '<p>9 уровней сложности · от нейрофизиологии до real-time BCI-системы</p>' +
          '<div class="tags-row">' +
          Object.entries(TAG_COLORS).map(([t,c]) =>
            '<span class="tag" style="color:' + c + ';background:' + c + '18;border:1px solid ' + c + '40">' + t + '</span>'
          ).join("") + '</div></div>';
        return;
      }}
      el.innerHTML = "";
      const wrap = document.createElement("div");
      wrap.innerHTML =
        '<div class="prob-header"><div class="prob-header-inner">' +
        '<div class="prob-icon" style="background:' + prob.color + '20;border:2px solid ' + prob.color + '60">' + prob.emoji + '</div>' +
        '<div style="flex:1"><div class="prob-badges">' +
        '<span class="badge">' + prob.id + '</span>' +
        '<span class="tag" style="color:' + prob.color + ';background:' + prob.color + '18;border:1px solid ' + prob.color + '40">' + prob.tag + '</span>' +
        '<span class="badge">Уровень ' + prob.level + ' · ' + prob.difficulty + '</span>' +
        '</div><h2 class="prob-h2">' + prob.title + '</h2></div>' +
        '<button class="btn-solved' + (solved[prob.id] ? " done" : "") + '" id="btn-solved">' +
        (solved[prob.id] ? "✓ Решено" : "○ Отметить") + '</button></div></div>' +
        '<div class="tabs"><button class="tab' + (tab === "problem" ? " active" : "") + '" data-tab="problem">📋 Задача</button>' +
        '<button class="tab' + (tab === "solution" ? " active" : "") + '" data-tab="solution" style="border-color:' + (tab === "solution" ? prob.color : "transparent") + '">💡 Ход решения</button></div>' +
        '<div class="content" id="prob-content"></div>';
      el.appendChild(wrap);
      document.getElementById("btn-solved").onclick = () => {{
        solved[prob.id] = !solved[prob.id];
        saveSolved();
        render();
      }};
      wrap.querySelectorAll(".tab").forEach(btn => {{
        btn.onclick = () => {{ tab = btn.dataset.tab; renderMain(); renderSidebar(); renderDots(); }};
        if (btn.dataset.tab === tab) btn.style.borderBottomColor = prob.color;
      }});
      const content = document.getElementById("prob-content");
      content.appendChild(renderContent(tab === "problem" ? prob.description : prob.solution));
    }}

    function render() {{
      document.getElementById("subtitle").textContent =
        PROBLEMS.length + " задач · от нейрофизиологии до real-time систем";
      renderDots();
      renderSidebar();
      renderMain();
    }}

    render();
  </script>
</body>
</html>
"""


def main():
    # Import problems from companion file
    import importlib.util
    spec_path = ROOT / "problems_data.py"
    if not spec_path.exists():
        raise SystemExit("Run: problems_data.py must exist")
    spec = importlib.util.spec_from_file_location("problems_data", spec_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    problems = mod.PROBLEMS
    level_names = mod.LEVEL_NAMES
    tag_colors = mod.TAG_COLORS

    html = HTML_TEMPLATE.replace("__PROBLEMS_JSON__", json.dumps(problems, ensure_ascii=False))
    html = html.replace("__LEVEL_NAMES_JSON__", json.dumps(level_names, ensure_ascii=False))
    html = html.replace("__TAG_COLORS_JSON__", json.dumps(tag_colors, ensure_ascii=False))
    OUT.write_text(html, encoding="utf-8")
    print(f"Wrote {OUT} ({OUT.stat().st_size // 1024} KB, {len(problems)} problems)")


if __name__ == "__main__":
    main()
