from aiogram import Router, Bot
from aiogram.filters import Command, command
from aiogram.types import Message

from filters.chat_types import ChatTypeFilter

user_group_router = Router()
user_group_router.message.filter(ChatTypeFilter(['group', 'supergroup']))


@user_group_router.message(Command(commands='admin'))
async def admin(message: Message, bot: Bot):
    chat_id = message.chat.id
    admins_list = await bot.get_chat_administrators(chat_id)

    admins_list = [member.user.id for member in admins_list if
                   member.status == 'creator' or member.status == 'administrator']

    bot.admins_list = admins_list

    if message.from_user.id in admins_list:
        await message.delete()
    else:
        await message.answer('You are not admin!')

