import asyncio
import logging
import os
from pathlib import Path

from aiohttp import web

from bot import main as bot_main

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

APP_ROOT = Path(__file__).resolve().parent / "nimbus-academy-app"


async def start_bot() -> None:
    logger.info("Запуск бота научного сообщества...")
    try:
        await bot_main()
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as exc:
        logger.error("Ошибка запуска бота: %s", exc)


async def health_check(_request: web.Request) -> web.Response:
    return web.Response(text="Bot is running!")


async def academy_index(_request: web.Request) -> web.FileResponse:
    return web.FileResponse(APP_ROOT / "index.html")


def setup_academy_routes(app: web.Application) -> None:
    if not APP_ROOT.exists():
        logger.warning("Nimbus Academy app folder not found: %s", APP_ROOT)
        return

    app.router.add_get("/", academy_index)
    app.router.add_get("/index.html", academy_index)

    for name in ("css", "js", "icons", "content"):
        path = APP_ROOT / name
        if path.exists():
            app.router.add_static(f"/{name}", path)

    for filename in ("manifest.json", "sw.js"):
        file_path = APP_ROOT / filename
        if file_path.exists():
            app.router.add_get(f"/{filename}", lambda _r, p=file_path: web.FileResponse(p))


async def main_web_service() -> None:
    asyncio.create_task(start_bot())

    app = web.Application()
    setup_academy_routes(app)
    app.router.add_get("/health", health_check)

    port_env = os.getenv("PORT", "8000")
    if port_env in ("$PORT",) or not str(port_env).isdigit():
        port = 8000
        logger.warning("Неверный PORT (%r), используем %s", port_env, port)
    else:
        port = int(port_env)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=port)
    await site.start()
    logger.info("Web + Nimbus Academy PWA: http://0.0.0.0:%s/", port)

    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main_web_service())
