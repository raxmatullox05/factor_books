from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_reply_keyboard(
        *btns,
        placeholder: str = None,
        request_contact: int = None,
        request_location: int = None,
        sizes: tuple[int] = (2,)
):
    keyboard = ReplyKeyboardBuilder()

    for i, text in enumerate(btns, start=0):
        if request_contact is not None and request_contact == i:
            keyboard.add(KeyboardButton(text=text, request_contact=True))
        elif request_location is not None and request_location == i:
            keyboard.add(KeyboardButton(text=text, request_location=True))
        else:
            keyboard.add(KeyboardButton(text=text))
    return keyboard.adjust(*sizes).as_markup(
        resize_keyboard=True, placeholder=placeholder
    )

