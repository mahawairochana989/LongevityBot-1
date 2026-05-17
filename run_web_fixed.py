import asyncio
import logging
import os
from aiohttp import web
from bot import main as bot_main

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def start_bot():
    """Starts the Telegram bot."""
    logger.info("Запуск бота научного сообщества...")
    try:
        await bot_main()
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Ошибка запуска бота: {e}")

async def health_check(request):
    """Simple health check endpoint."""
    return web.Response(text="Bot is running!")

async def main_web_service():
    """Main function to run the bot as a web service."""
    # Start the bot in the background
    asyncio.create_task(start_bot())

    # Setup a simple web server for health checks (required by Render Web Service)
    app = web.Application()
    app.router.add_get('/health', health_check)

    # Обработка порта с защитой от $PORT
    port_env = os.getenv("PORT", "8000")
    logger.info(f"Получен PORT из окружения: '{port_env}'")
    
    if port_env == '$PORT' or port_env == '$PORT' or not str(port_env).isdigit():
        PORT = 8000
        logger.warning(f"Неверный формат PORT ('{port_env}'), используем {PORT}")
    else:
        try:
            PORT = int(port_env)
            logger.info(f"Используем PORT: {PORT}")
        except (ValueError, TypeError):
            PORT = 8000
            logger.warning(f"Ошибка преобразования PORT ('{port_env}'), используем {PORT}")
    
    logger.info(f"Web Service будет доступен на порту: {PORT}")
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=PORT)
    await site.start()
    logger.info(f"Web Service запущен на http://0.0.0.0:{PORT}")

    # Keep the main task running indefinitely
    while True:
        await asyncio.sleep(3600) # Sleep for an hour, or until interrupted

if __name__ == "__main__":
    asyncio.run(main_web_service())
