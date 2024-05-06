import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommandScopeChat
# from aiogram.utils.i18n import I18n, FSMI18nMiddleware

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
    await create_db()

    await bot.set_my_commands(user_commands)
    await bot.delete_my_commands()

    for admin_id in bot.admins_list:
        scope = BotCommandScopeChat(chat_id=admin_id)
        await bot.set_my_commands(admin_commands, scope)


async def on_shutdown():

    print('Shutting down...')


async def main():
    # i18n = I18n(path='locales', default_locale="en", domain='messages')
    # dp.message.outer_middleware(FSMI18nMiddleware(i18n))
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
