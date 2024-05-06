from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.i18n import gettext as _



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


ikar_kb = {"⚡IKAR": "⚡IKAR",
           "📚 Factor books kitoblari": "📚 Factor books kitoblari",
           "Biznes kitoblar": "Biznes kitoblar",
           "Diniy kitoblar": "Diniy kitoblar",
           "📚 Boshqa kitoblar": "📚 Boshqa kitoblar",
           "Psixologik kitoblar": "Psixologik kitoblar",
           "Tarbiyaviy-oilaviy kitoblar": "Tarbiyaviy-oilaviy kitoblar",
           "Turk badiiy-ma'rifiy kitoblar": "Turk badiiy-ma'rifiy kitoblar",
           "Badiiy Romanlar": "Badiiy Romanlar",
           "QIssa va Romanlar": "Qissa va Romanlar",
           "Badiiy kitoblar va qissalar": "Badiiy kitoblar va qissalar",
           "🔍 Qidirish": "🔍 Qidirish"}
