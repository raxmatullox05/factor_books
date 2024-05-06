import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommandScopeChat

from common.cmd_list import admin_commands, user_commands
from config import TOKEN, start_router
from database.engine import session_maker, create_db
from middlewares.db import DataBaseSession

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
bot.admins_list = []

dp = Dispatcher()
dp.include_routers(start_router)


async def on_startup():
    # await drop_db()
    await bot.set_my_commands(user_commands)

    ADMIN_LIST = [2039584148]
    for admin_id in ADMIN_LIST:
        scope = BotCommandScopeChat(chat_id=admin_id)
        await bot.set_my_commands(admin_commands, scope)

    # await create_db()


async def on_shutdown():
    print('Shutting down...')


async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
