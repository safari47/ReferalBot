import asyncio
from aiogram.types import BotCommand, BotCommandScopeDefault
from loguru import logger
from handlers.admin import router as admin_router
from handlers.user import router as user_router
from config.config import bot, dp
from db.base import create_tables


# Функция, которая настроит командное меню (дефолтное для всех пользователей)
async def set_commands():
    commands = [BotCommand(command="start", description="Старт")]
    await bot.set_my_commands(commands, BotCommandScopeDefault())


# Функция, которая выполнится когда бот запустится
async def start_bot():
    await set_commands()
    await create_tables()
    logger.info("Бот успешно запущен.")


# Функция, которая выполнится когда бот завершит свою работу
async def stop_bot():

    logger.error("Бот остановлен!")


async def main():
    dp.include_router(admin_router)
    dp.include_router(user_router)

    # регистрация функций
    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)
    # запуск бота в режиме long polling при запуске бот очищает все обновления, которые были за его моменты бездействия
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
