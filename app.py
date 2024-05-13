import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.utils.i18n import I18n, FSMI18nMiddleware

from common.cmd_list import user_commands
from common.routers import start_router
from config import TOKEN
from database.engine import session_maker, create_db, drop_db
from middlewares.db import DataBaseSession

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
bot.admins_list = []

dp = Dispatcher()
dp.include_routers(start_router)


async def on_startup():
    # await drop_db()
    await create_db()
    await bot.set_my_commands(user_commands)


async def on_shutdown():
    await bot.delete_my_commands()


async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    i18n = I18n(path='locales')
    dp.update.outer_middleware(FSMI18nMiddleware(i18n))
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
