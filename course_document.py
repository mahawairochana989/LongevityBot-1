#!/usr/bin/env python3
"""
Presentation-ready course program document for the longevity community.
"""

from datetime import date
from html import escape
from typing import Iterable

from config import ADMIN_USERNAME, EDUCATION_LEVELS, SCIENTIFIC_DISCIPLINES


COURSE_DOCUMENT_FILENAME = "longevity-course-program.html"
COURSE_TITLE = "Научное сообщество по продлению жизни"
COURSE_SUBTITLE = "Программа курса по биологии старения, эпигенетике и применению ИИ в исследованиях долголетия"

PROGRAM_MODULES = [
    {
        "number": "01",
        "title": "Введение в биологию старения",
        "focus": "Единая научная рамка для участников из разных дисциплин.",
        "topics": [
            "ключевые механизмы старения и hallmarks of aging",
            "роль клеточной сенесценции, воспаления и стресса",
            "как читать и обсуждать современные статьи по долголетию",
        ],
        "result": "Участники говорят на общем языке и понимают базовые модели старения.",
    },
    {
        "number": "02",
        "title": "Генетика, геномика и эпигенетика долголетия",
        "focus": "Связь наследственности, регуляции генов и возрастных изменений.",
        "topics": [
            "эпигенетические часы и биомаркеры возраста",
            "геномные и транскриптомные данные в исследованиях старения",
            "интерпретация результатов омисных исследований",
        ],
        "result": "Участники умеют разбирать статьи с генетическими и эпигенетическими данными.",
    },
    {
        "number": "03",
        "title": "Нейробиология, иммунология и физиология старения",
        "focus": "Системный взгляд на возрастные изменения организма.",
        "topics": [
            "старение мозга и когнитивные функции",
            "иммунное старение и хроническое воспаление",
            "физиологические маркеры риска и здоровья",
        ],
        "result": "Участники видят, как разные системы организма связаны в исследованиях долголетия.",
    },
    {
        "number": "04",
        "title": "ИИ, биоинформатика и вычислительная биология",
        "focus": "Практическое применение данных и моделей для поиска гипотез.",
        "topics": [
            "машинное обучение в биомедицине",
            "анализ научных публикаций и подбор релевантных статей",
            "поиск паттернов в биологических и клинических данных",
        ],
        "result": "Участники понимают, где ИИ действительно помогает исследователю, а где нужны ограничения.",
    },
    {
        "number": "05",
        "title": "Фармакология, биотехнологии и трансляционные исследования",
        "focus": "Переход от гипотез к интервенциям и проверяемым протоколам.",
        "topics": [
            "геропротекторы, биотехнологические подходы и ограничения доказательности",
            "дизайн доклинических и клинических исследований",
            "регуляторика, безопасность и этика исследований",
        ],
        "result": "Участники оценивают перспективность интервенций по качеству доказательств.",
    },
    {
        "number": "06",
        "title": "Междисциплинарные команды и исследовательские разборы",
        "focus": "Коллаборации между биологами, медиками, математиками и ИИ-специалистами.",
        "topics": [
            "формирование команд по интересам и дисциплинам",
            "разбор статей в формате journal club",
            "подготовка мини-проектов и исследовательских гипотез",
        ],
        "result": "Участники получают партнеров для обсуждений и основу для будущих совместных проектов.",
    },
]

FORMAT_POINTS = [
    "регулярные онлайн-встречи и семинары",
    "междисциплинарные команды для обсуждения научных статей",
    "подбор коллег по дисциплинам, интересам и уровню подготовки",
    "обсуждение актуальных исследований в области долголетия",
    "сетевые возможности для научных коллабораций",
]

AUDIENCE_POINTS = [
    "студенты бакалавриата и магистратуры",
    "аспиранты и молодые исследователи",
    "преподаватели и специалисты биомедицинских направлений",
    "участники из вычислительных, математических и ИИ-направлений",
]

OUTCOME_POINTS = [
    "понимание ключевых направлений современной науки о старении",
    "навык критического чтения и обсуждения научных публикаций",
    "карта перспективных тем для личного исследования или командного проекта",
    "контакты участников из смежных областей для дальнейших коллабораций",
]


def _render_list(items: Iterable[str]) -> str:
    return "\n".join(f"<li>{escape(item)}</li>" for item in items)


def _render_badges(items: Iterable[str]) -> str:
    return "\n".join(f'<span class="badge">{escape(item)}</span>' for item in items)


def _render_modules() -> str:
    cards = []
    for module in PROGRAM_MODULES:
        topics = _render_list(module["topics"])
        cards.append(
            f"""
            <article class="module-card">
                <div class="module-number">{escape(module["number"])}</div>
                <div>
                    <p class="eyebrow">Модуль</p>
                    <h3>{escape(module["title"])}</h3>
                    <p class="module-focus">{escape(module["focus"])}</p>
                    <ul>{topics}</ul>
                    <div class="result"><strong>Итог:</strong> {escape(module["result"])}</div>
                </div>
            </article>
            """
        )
    return "\n".join(cards)


def render_course_summary() -> str:
    """Short Markdown-friendly summary for Telegram messages."""
    return (
        f"📘 **{COURSE_TITLE}**\n\n"
        f"{COURSE_SUBTITLE}\n\n"
        "Документ включает цели курса, формат, модули, направления участников, "
        "ожидаемые результаты и контакт для связи."
    )


def render_course_document(download_path: str = "/course/download") -> str:
    """Return a styled, standalone HTML document."""
    generated_on = date.today().strftime("%d.%m.%Y")
    modules_html = _render_modules()
    disciplines_html = _render_badges(SCIENTIFIC_DISCIPLINES)
    education_html = _render_badges(EDUCATION_LEVELS)

    return f"""<!doctype html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{escape(COURSE_TITLE)} — программа курса</title>
    <style>
        :root {{
            color-scheme: light;
            --bg: #f5f7fb;
            --ink: #14213d;
            --muted: #5d6475;
            --card: rgba(255, 255, 255, 0.92);
            --line: rgba(20, 33, 61, 0.11);
            --primary: #2f80ed;
            --primary-dark: #1057b4;
            --accent: #00b894;
            --violet: #7257ff;
            --gold: #f9ab00;
            --shadow: 0 24px 70px rgba(25, 42, 86, 0.16);
        }}

        * {{
            box-sizing: border-box;
        }}

        body {{
            margin: 0;
            font-family: Inter, "Segoe UI", Roboto, Arial, sans-serif;
            color: var(--ink);
            background:
                radial-gradient(circle at 12% 8%, rgba(47, 128, 237, 0.20), transparent 32rem),
                radial-gradient(circle at 88% 0%, rgba(0, 184, 148, 0.18), transparent 30rem),
                linear-gradient(135deg, #f8fbff 0%, var(--bg) 48%, #eef4ff 100%);
            line-height: 1.58;
        }}

        .page {{
            width: min(1180px, calc(100% - 36px));
            margin: 0 auto;
            padding: 34px 0 56px;
        }}

        .hero {{
            position: relative;
            overflow: hidden;
            padding: clamp(34px, 6vw, 78px);
            border: 1px solid rgba(255, 255, 255, 0.72);
            border-radius: 34px;
            background:
                linear-gradient(135deg, rgba(20, 33, 61, 0.95), rgba(16, 87, 180, 0.88)),
                radial-gradient(circle at 78% 18%, rgba(0, 184, 148, 0.45), transparent 24rem);
            color: #fff;
            box-shadow: var(--shadow);
        }}

        .hero::after {{
            content: "";
            position: absolute;
            inset: auto -80px -140px auto;
            width: 380px;
            height: 380px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(255, 255, 255, 0.18), transparent 66%);
        }}

        .hero-content {{
            position: relative;
            z-index: 1;
            max-width: 860px;
        }}

        .label {{
            display: inline-flex;
            gap: 10px;
            align-items: center;
            padding: 8px 14px;
            border: 1px solid rgba(255, 255, 255, 0.32);
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.12);
            color: rgba(255, 255, 255, 0.92);
            font-size: 14px;
            letter-spacing: 0.02em;
        }}

        h1 {{
            max-width: 900px;
            margin: 24px 0 18px;
            font-size: clamp(38px, 7vw, 78px);
            line-height: 0.98;
            letter-spacing: -0.055em;
        }}

        .subtitle {{
            max-width: 760px;
            margin: 0;
            color: rgba(255, 255, 255, 0.84);
            font-size: clamp(18px, 2.2vw, 25px);
        }}

        .hero-actions {{
            display: flex;
            flex-wrap: wrap;
            gap: 14px;
            margin-top: 34px;
        }}

        .button {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-height: 48px;
            padding: 13px 19px;
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.28);
            color: #fff;
            text-decoration: none;
            font-weight: 700;
            background: linear-gradient(135deg, var(--accent), #20c997);
            box-shadow: 0 14px 30px rgba(0, 184, 148, 0.24);
        }}

        .button.secondary {{
            background: rgba(255, 255, 255, 0.12);
            box-shadow: none;
        }}

        .stats {{
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 16px;
            margin: 22px 0;
        }}

        .stat-card, .section, .module-card {{
            border: 1px solid var(--line);
            background: var(--card);
            box-shadow: 0 18px 54px rgba(25, 42, 86, 0.08);
            backdrop-filter: blur(14px);
        }}

        .stat-card {{
            padding: 22px;
            border-radius: 24px;
        }}

        .stat-value {{
            display: block;
            color: var(--primary-dark);
            font-size: 32px;
            font-weight: 850;
            letter-spacing: -0.04em;
        }}

        .stat-label {{
            color: var(--muted);
            font-size: 14px;
        }}

        .section {{
            margin-top: 22px;
            padding: clamp(24px, 4vw, 40px);
            border-radius: 30px;
        }}

        .section-grid {{
            display: grid;
            grid-template-columns: 0.85fr 1.15fr;
            gap: clamp(22px, 4vw, 44px);
            align-items: start;
        }}

        .eyebrow {{
            margin: 0 0 8px;
            color: var(--primary);
            font-size: 12px;
            font-weight: 800;
            letter-spacing: 0.16em;
            text-transform: uppercase;
        }}

        h2, h3 {{
            margin: 0;
            letter-spacing: -0.03em;
        }}

        h2 {{
            font-size: clamp(28px, 4vw, 46px);
            line-height: 1.05;
        }}

        h3 {{
            font-size: 24px;
            line-height: 1.18;
        }}

        .lead {{
            color: var(--muted);
            font-size: 18px;
        }}

        .check-list {{
            display: grid;
            gap: 12px;
            margin: 0;
            padding: 0;
            list-style: none;
        }}

        .check-list li {{
            position: relative;
            padding: 13px 16px 13px 44px;
            border-radius: 16px;
            background: #f7faff;
            border: 1px solid rgba(47, 128, 237, 0.10);
        }}

        .check-list li::before {{
            content: "";
            position: absolute;
            left: 17px;
            top: 19px;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: linear-gradient(135deg, var(--accent), var(--primary));
        }}

        .modules {{
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 18px;
            margin-top: 26px;
        }}

        .module-card {{
            display: grid;
            grid-template-columns: auto 1fr;
            gap: 18px;
            padding: 24px;
            border-radius: 26px;
        }}

        .module-number {{
            display: grid;
            place-items: center;
            width: 58px;
            height: 58px;
            border-radius: 20px;
            color: #fff;
            font-size: 20px;
            font-weight: 850;
            background: linear-gradient(135deg, var(--primary), var(--violet));
            box-shadow: 0 12px 28px rgba(47, 128, 237, 0.24);
        }}

        .module-focus {{
            color: var(--muted);
            margin: 8px 0 12px;
        }}

        .module-card ul {{
            margin: 0;
            padding-left: 20px;
        }}

        .result {{
            margin-top: 14px;
            padding: 12px 14px;
            border-radius: 16px;
            background: rgba(0, 184, 148, 0.10);
            color: #0d5d50;
        }}

        .badges {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }}

        .badge {{
            display: inline-flex;
            align-items: center;
            min-height: 38px;
            padding: 8px 13px;
            border-radius: 999px;
            color: #24324b;
            background: #ffffff;
            border: 1px solid rgba(20, 33, 61, 0.10);
            box-shadow: 0 10px 22px rgba(20, 33, 61, 0.06);
            font-size: 14px;
            font-weight: 650;
        }}

        .timeline {{
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 16px;
        }}

        .timeline-step {{
            padding: 20px;
            border-radius: 22px;
            background: linear-gradient(180deg, #ffffff, #f8fbff);
            border: 1px solid var(--line);
        }}

        .timeline-step strong {{
            display: block;
            margin-bottom: 8px;
            color: var(--primary-dark);
        }}

        .footer {{
            display: flex;
            flex-wrap: wrap;
            gap: 18px;
            align-items: center;
            justify-content: space-between;
            margin-top: 22px;
            padding: 24px 28px;
            border-radius: 28px;
            color: #fff;
            background: linear-gradient(135deg, var(--ink), #263b6f);
        }}

        .footer p {{
            margin: 0;
            color: rgba(255, 255, 255, 0.78);
        }}

        .print-note {{
            color: var(--muted);
            font-size: 13px;
        }}

        @media (max-width: 900px) {{
            .stats, .modules, .timeline, .section-grid {{
                grid-template-columns: 1fr;
            }}

            .hero {{
                border-radius: 26px;
            }}
        }}

        @media print {{
            body {{
                background: #fff;
            }}

            .page {{
                width: 100%;
                padding: 0;
            }}

            .button {{
                display: none;
            }}

            .hero, .section, .stat-card, .module-card, .footer {{
                box-shadow: none;
                break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <main class="page">
        <section class="hero">
            <div class="hero-content">
                <span class="label">Презентационный документ • обновлено {generated_on}</span>
                <h1>{escape(COURSE_TITLE)}</h1>
                <p class="subtitle">{escape(COURSE_SUBTITLE)}</p>
                <div class="hero-actions">
                    <a class="button" href="{escape(download_path)}">Скачать документ</a>
                    <a class="button secondary" href="javascript:window.print()">Открыть печать / PDF</a>
                </div>
            </div>
        </section>

        <section class="stats" aria-label="Ключевые параметры курса">
            <div class="stat-card">
                <span class="stat-value">{len(PROGRAM_MODULES)}</span>
                <span class="stat-label">тематических модулей</span>
            </div>
            <div class="stat-card">
                <span class="stat-value">{len(SCIENTIFIC_DISCIPLINES)}</span>
                <span class="stat-label">научных направлений</span>
            </div>
            <div class="stat-card">
                <span class="stat-value">{len(EDUCATION_LEVELS)}</span>
                <span class="stat-label">уровней подготовки</span>
            </div>
            <div class="stat-card">
                <span class="stat-value">online</span>
                <span class="stat-label">формат встреч</span>
            </div>
        </section>

        <section class="section section-grid">
            <div>
                <p class="eyebrow">Цель</p>
                <h2>Собрать междисциплинарное сообщество вокруг науки о долголетии</h2>
                <p class="lead">
                    Курс помогает студентам, молодым ученым и специалистам регулярно обсуждать
                    научные статьи по биологии старения, эпигенетике и применению ИИ в продлении жизни.
                </p>
            </div>
            <ul class="check-list">
                {_render_list(FORMAT_POINTS)}
            </ul>
        </section>

        <section class="section">
            <p class="eyebrow">Программа</p>
            <h2>Модули курса</h2>
            <div class="modules">
                {modules_html}
            </div>
        </section>

        <section class="section section-grid">
            <div>
                <p class="eyebrow">Для кого</p>
                <h2>Участники и уровни подготовки</h2>
                <p class="lead">
                    Программа рассчитана на людей с разным академическим опытом: от студентов
                    до преподавателей и исследователей, которым интересны биомедицина,
                    вычислительные методы и коллаборации.
                </p>
                <div class="badges">{education_html}</div>
            </div>
            <ul class="check-list">
                {_render_list(AUDIENCE_POINTS)}
            </ul>
        </section>

        <section class="section">
            <p class="eyebrow">Направления</p>
            <h2>Дисциплины для междисциплинарных команд</h2>
            <p class="lead">
                Участники подбираются по научным интересам и дисциплинам, чтобы обсуждения
                соединяли биологию, медицину, математику, ИИ и инженерные подходы.
            </p>
            <div class="badges">{disciplines_html}</div>
        </section>

        <section class="section section-grid">
            <div>
                <p class="eyebrow">Результаты</p>
                <h2>Что получает участник</h2>
                <p class="lead">
                    Курс сфокусирован не только на знаниях, но и на практическом навыке
                    научного обсуждения, поиске гипотез и создании профессиональных связей.
                </p>
            </div>
            <ul class="check-list">
                {_render_list(OUTCOME_POINTS)}
            </ul>
        </section>

        <section class="section">
            <p class="eyebrow">Маршрут участия</p>
            <h2>Как подключиться</h2>
            <div class="timeline">
                <div class="timeline-step">
                    <strong>1. Заполнить анкету</strong>
                    Участник указывает имя, университет, дисциплину, научные интересы и уровень подготовки.
                </div>
                <div class="timeline-step">
                    <strong>2. Получить подбор</strong>
                    Бот помогает найти коллег для обсуждений и междисциплинарных команд.
                </div>
                <div class="timeline-step">
                    <strong>3. Участвовать во встречах</strong>
                    Команды обсуждают статьи, формируют гипотезы и развивают будущие коллаборации.
                </div>
            </div>
        </section>

        <footer class="footer">
            <div>
                <strong>Контакт для связи: {escape(ADMIN_USERNAME)}</strong>
                <p>Документ можно демонстрировать в браузере, скачать как HTML или сохранить в PDF через печать.</p>
            </div>
            <a class="button" href="{escape(download_path)}">Скачать программу</a>
        </footer>
        <p class="print-note">Если нужен PDF-файл: нажмите «Открыть печать / PDF» и выберите «Сохранить в PDF».</p>
    </main>
</body>
</html>
"""
