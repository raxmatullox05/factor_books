from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_inline_keyboard(
        *,
        btns: dict[str, str],
        sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()

    for text, value in btns.items():
        if '://' in value:
            keyboard.add(InlineKeyboardButton(text=text, url=value))
        elif value == "switch_inline_query_current_chat":
            keyboard.add(InlineKeyboardButton(text=text, switch_inline_query_current_chat=' '))
        else:
            keyboard.add(InlineKeyboardButton(text=text, callback_data=value))
    return keyboard.adjust(*sizes).as_markup()