#!/usr/bin/env python3
"""Build EPUB: Japanese text + vocabulary list for each section."""

import json
from datetime import date
from pathlib import Path

from ebooklib import epub

ROOT = Path(__file__).parent
SECTIONS_DIR = ROOT / "sections"
OUT = ROOT / "japanese-vocabulary-reader.epub"


def load_sections() -> list[dict]:
    sections = []
    for path in sorted(SECTIONS_DIR.glob("*.json")):
        sections.append(json.loads(path.read_text(encoding="utf-8")))
    return sections


def vocab_table(vocab: list[dict]) -> str:
    rows = []
    for i, item in enumerate(vocab, 1):
        rows.append(
            f"<tr><td>{i}</td><td>{item['word']}</td>"
            f"<td>{item['reading']}</td><td>{item['ru']}</td></tr>"
        )
    return (
        "<table class='vocab'>"
        "<thead><tr><th>#</th><th>語</th><th>読み</th><th>Русский</th></tr></thead>"
        "<tbody>" + "".join(rows) + "</tbody></table>"
    )


def section_html(sec: dict, index: int) -> str:
    title = sec.get("title_ja") or sec.get("title_ru", f"Section {index}")
    text = sec["text_ja"].replace("\n\n", "</p><p>").replace("\n", "<br/>")
    vocab = vocab_table(sec["vocabulary"])
    return f"""
<section id="sec-{sec['id']}" class="section">
  <h1>{index}. {title}</h1>
  <h2 class="label">テキスト</h2>
  <div class="japanese"><p>{text}</p></div>
  <h2 class="label">語彙リスト</h2>
  {vocab}
</section>
"""


def build() -> None:
    sections = load_sections()
    if not sections:
        raise SystemExit("No sections in sections/")

    book = epub.EpubBook()
    book.set_identifier("japanese-vocabulary-reader")
    book.set_title("日本語語彙リーダー · Japanese Vocabulary Reader")
    book.set_language("ja")
    book.add_author("Nimbus Academy")

    css = epub.EpubItem(
        uid="style",
        file_name="style.css",
        media_type="text/css",
        content="""
body { font-family: "Hiragino Sans", "Noto Sans JP", sans-serif; line-height: 1.8; margin: 1em; }
h1 { font-size: 1.4em; border-bottom: 2px solid #333; padding-bottom: 0.3em; }
h2.label { font-size: 1.1em; color: #555; margin-top: 1.5em; }
.japanese { font-size: 1.05em; background: #f8f8f8; padding: 1em; border-radius: 8px; }
table.vocab { width: 100%; border-collapse: collapse; font-size: 0.95em; margin-top: 0.5em; }
table.vocab th, table.vocab td { border: 1px solid #ccc; padding: 0.45em 0.6em; text-align: left; }
table.vocab th { background: #eee; }
table.vocab td:nth-child(2) { font-weight: bold; }
.section { page-break-after: always; margin-bottom: 2em; }
.intro { color: #666; font-size: 0.9em; }
""".strip().encode("utf-8"),
    )
    book.add_item(css)

    intro = epub.EpubHtml(
        title="はじめに",
        file_name="intro.xhtml",
        lang="ja",
    )
    intro.content = f"""
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>Intro</title><link rel="stylesheet" href="style.css"/></head>
<body>
  <h1>日本語語彙リーダー</h1>
  <p class="intro">各セクション：日本語テキスト → 語彙リスト（ひらがな + ロシア語）</p>
  <p class="intro">更新日: {date.today().isoformat()} · セクション数: {len(sections)}</p>
</body></html>
"""
    book.add_item(intro)

    chapters = [intro]
    spine_items = ["nav", intro]

    for i, sec in enumerate(sections, 1):
        ch = epub.EpubHtml(
            title=sec.get("title_ja", sec["id"]),
            file_name=f"chapter_{i:02d}.xhtml",
            lang="ja",
        )
        ch.content = f"""
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>{sec.get('title_ja', '')}</title>
<link rel="stylesheet" href="style.css"/></head>
<body>
{section_html(sec, i)}
</body></html>
"""
        book.add_item(ch)
        chapters.append(ch)
        spine_items.append(ch)

    book.toc = chapters
    book.spine = spine_items
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    epub.write_epub(str(OUT), book)
    print(f"Wrote {OUT} ({OUT.stat().st_size // 1024} KB, {len(sections)} section(s))")


if __name__ == "__main__":
    build()
