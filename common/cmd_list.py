from aiogram.types import BotCommand

user_commands = (
    BotCommand(command='start', description='Start the bot'),
    BotCommand(command='help', description='Do you need a help?'),
)

admin_commands = (
    BotCommand(command='add_category', description='Add category'),
    BotCommand(command='add_product', description='Add product'),
)
