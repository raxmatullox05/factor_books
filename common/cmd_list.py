from aiogram.types import BotCommand

user_commands = (
    BotCommand(command='start', description='Start the bot'),
    BotCommand(command='help', description='Do you need a help?'),
)

admin_commands = (
    BotCommand(command='start', description='Start the bot'),
    BotCommand(command='add a product', description='Add a new product'),
    BotCommand(command='show all products', description='Show all products'),
    BotCommand(command='cancel', description='To cancel the process of adding a new product'),
    BotCommand(command='step over', description='Make one step over')
)
