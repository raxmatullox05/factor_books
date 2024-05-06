from aiogram import Router, html, F
from aiogram.enums import ChatType
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, message
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import orm_get_categories, orm_get_category, orm_get_products, orm_get_product, orm_add_user, \
    orm_add_to_cart, orm_get_user_cart, orm_clear_cart
from filters.chat_types import ChatTypeFilter
from keyboards.inline_keyboards import get_inline_keyboard
from keyboards.reply_keyboards import get_reply_keyboard

# from aiogram.utils.i18n import gettext as _
# from aiogram.utils.i18n import lazy_gettext as __

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter([ChatType.PRIVATE]))


@user_private_router.message(CommandStart())
async def start(message: Message):
    await message.answer(text=f'Hello {message.from_user.full_name}! Choose.',
                         reply_markup=get_reply_keyboard(
                             "📚 Kitoblar",
                             "📃 Mening buyurtmalarim",
                             "🔵 Biz ijtimoiy tarmoqlarda",
                             "📞 Biz bilan bog'lanish",
                             sizes=(1, 1, 2)
                         ))


@user_private_router.message(F.text == "📚 Kitoblar")
async def kitoblar(message: Message, session: AsyncSession):
    categories = await orm_get_categories(session)
    btns = {category.name: f"category_{category.id}" for category in categories}
    btns['🔍 Qidirish'] = "switch_inline_query_current_chat"
    cart = await orm_get_user_cart(session, message.from_user.id)
    if cart:
        btns[f'🛒 Savat({cart[0].quantity})'] = f"savat_{message.from_user.id}"
    await message.answer("Qaysi categoriyalarni product larini ko'rmoxchisiz: ",
                         reply_markup=get_inline_keyboard(btns=btns))


# @user_private_router.message(F.text == '🌐 Change language')
# async def change_language(message: Message):
#     await message.answer('Choose language', reply_markup=get_inline_keyboard(btns={
#         "uz": "lang_uz",
#         "en": "lang_en"
#     }, sizes=(1,)))


# @user_private_router.callback_query(F.data.startswith('lang'))
# async def start_handler(callback: CallbackQuery, state: FSMContext):
#     lang_code = callback.data.split('_')[-1]
#     await state.set_data({'locales': lang_code})
#     await callback.answer(_('Language chosen', locale=lang_code))


@user_private_router.callback_query(F.data == 'back')
async def back(callback: CallbackQuery, session: AsyncSession):
    await callback.answer()
    categories = await orm_get_categories(session)
    btns = {category.name: f"category_{category.id}" for category in categories}
    cart = await orm_get_user_cart(session, callback.from_user.id)
    if cart:
        btns[f'🛒 Savat({cart[0].quantity})'] = f"savat_{callback.from_user.id}"
    await callback.message.edit_text("Kategoriyalardan birini tanlang: ",
                                     reply_markup=get_inline_keyboard(btns=btns))


@user_private_router.callback_query(F.data == 'backback')
async def backback(callback: CallbackQuery, session: AsyncSession):
    await callback.answer()
    await callback.message.delete()
    categories = await orm_get_categories(session)
    btns = {category.name: f"category_{category.id}" for category in categories}
    cart = await orm_get_user_cart(session, callback.from_user.id)
    if cart:
        btns[f'🛒 Savat({cart[0].quantity})'] = f"savat_{callback.from_user.id}"
    await callback.message.answer("Kategoriyalardan birini tanlang: ",
                                  reply_markup=get_inline_keyboard(btns=btns))


@user_private_router.callback_query(F.data.startswith('category_'))
async def show_products_of_category(callback: CallbackQuery, session: AsyncSession):
    category = int(callback.data.split('_')[-1])
    category_name = await orm_get_category(session, category)
    products = await orm_get_products(session, category)
    btns = {product.nomi: f"product_{product.id}" for product in products}
    btns['⬅ Orqaga'] = 'back'
    await callback.message.edit_text(f"{category_name.name}", reply_markup=get_inline_keyboard(btns=btns))


async def make_plus_minus(product_id, session: AsyncSession, amount: int = 1):
    product = await orm_get_product(session, int(product_id))
    reply_markup = get_inline_keyboard(btns={
        "➖": f"op_minus_{product.id}_{amount}",
        f"{amount}": f"current{amount}",
        "➕": f"op_plus_{product.id}_{amount}",
        "⬅ Orqaga": "backback",
        "🛒 Savatga qo'shish": f"basket_{product.id}_{amount}"
    }, sizes=(3, 2))
    return reply_markup


@user_private_router.callback_query(F.data.startswith('product_'))
async def show_product_of_category(callback: CallbackQuery, session: AsyncSession, amount: int = 1):
    product_id = callback.data.split('_')[-1]
    product = await orm_get_product(session, int(product_id))
    photo = product.rasmi
    caption = f"""🔷 Nomi: {product.nomi}\nMuallifi: {product.muallifi}\nJanri: {product.janri}\nTarjimon: {product.tarjimon}\nBet: {product.bet}\nMuqova: {product.muqova}\n💸 Narxi: {product.narxi} so'm"""
    await callback.message.answer_photo(photo=photo, caption=caption,
                                        reply_markup=await make_plus_minus(product_id, session))
    await callback.message.delete()


@user_private_router.callback_query(F.data.startswith('op'))
async def operations(callback: CallbackQuery, session: AsyncSession):
    product_id = callback.data.split('_')[2]
    operation = callback.data.split('_')[1]
    amount = int(callback.data.split('_')[-1])
    product = await orm_get_product(session, int(product_id))
    photo = product.rasmi
    caption = f"""🔷 Nomi: {product.nomi}\nMuallifi: {product.muallifi}\nJanri: {product.janri}\nTarjimon: {product.tarjimon}\nBet: {product.bet}\nMuqova: {product.muqova}\n💸 Narxi: {product.narxi} so'm"""
    media = InputMediaPhoto(media=photo, caption=caption, has_spoiler=True)

    if operation == 'minus':
        await callback.message.edit_media(media, reply_markup=await make_plus_minus(product_id, session, amount - 1))

    else:
        await callback.message.edit_media(media, reply_markup=await make_plus_minus(product_id, session, amount + 1))


@user_private_router.callback_query(F.data.startswith('basket_'))
async def add_to_cart(callback: CallbackQuery, session: AsyncSession):
    await callback.answer()
    user = callback.from_user
    await orm_add_user(
        session,
        user.id,
        user.first_name,
        user.last_name
    )

    product_id = callback.data.split('_')[1]
    amount = callback.data.split("_")[-1]
    await orm_add_to_cart(session, user.id, int(product_id), int(amount))
    await callback.answer("Product qo'shildi", show_alert=True)
    await callback.message.delete()
    categories = await orm_get_categories(session)
    btns = {category.name: f"category_{category.id}" for category in categories}
    cart = await orm_get_user_cart(session, callback.from_user.id)
    if cart:
        btns[f'🛒 Savat({len(cart)})'] = f"savat_{callback.from_user.id}"
    await callback.message.answer("Qaysi categoriyalarni product larini ko'rmoxchisiz: ",
                                  reply_markup=get_inline_keyboard(btns=btns))


@user_private_router.callback_query(F.data.startswith('savat'))
async def savat_info(callback: CallbackQuery, session: AsyncSession):
    user_id = callback.data.split('_')[-1]
    carts = await orm_get_user_cart(session, int(user_id))
    if carts:
        msg = "🛒 Savat\n\n"
        summa = 0
        for i, cart in enumerate(carts, start=1):
            product = await orm_get_product(session, cart.product_id)
            msg += f"{i}. {product.nomi}\n{cart.quantity} x {product.narxi} = {cart.quantity * product.narxi} so'm\n\n"
            summa += cart.quantity * product.narxi
        msg += f"Jami: {summa} so'm"

    await callback.message.edit_text(msg, reply_markup=get_inline_keyboard(btns={
        "❌ Savatni tozalash": f"cart_tozalash_{user_id}",
        "✅ Buyurtmani tasdiqlash": f"cart_savat_tasdiqlash_{user_id}",
        "⬅ Orqaga": "back"
    }, sizes=(1,)))


@user_private_router.callback_query(F.data.startswith('cart'))
async def savat_operations(callback: CallbackQuery, session: AsyncSession):
    user_id = callback.data.split('_')[-1]
    if callback.data.split('_')[1] == 'tozalash':
        await callback.answer()
        await orm_clear_cart(session, int(user_id))
        await back(callback, session)
    else:
        await callback.message.answer('📞 Telefon raqam tugmasini bosing 🔽:',
                                      reply_markup=get_reply_keyboard('📞 Telefon raqam', request_contact=0))


@user_private_router.message(F.contact)
async def add_contact_to_user(message: Message, session: AsyncSession):
    user_id = message.from_user.id
    carts = await orm_get_user_cart(session, user_id)
    if carts:
        msg = "🛒 Savat\n\n"
        summa = 0
        for i, cart in enumerate(carts, start=1):
            product = await orm_get_product(session, cart.product_id)
            msg += f"{i}. {product.nomi}\n{cart.quantity} x {product.narxi} = {cart.quantity * product.narxi} so'm\n\n"
            summa += cart.quantity * product.narxi
        msg += f"Jami: {summa} so'm\nTelfon raqamingiz: {message.contact.phone_number}\n\nBuyurtma berasizmi?"

    await message.answer(msg, reply_markup=get_inline_keyboard(btns={
        "❌ Yo'q": f"finish_bekor_{user_id}",
        "✅ Ha": f"finish_tayyor_{user_id}",
        "⬅ Orqaga": "back"
    }, sizes=(1,)))


@user_private_router.callback_query(F.data.startswith('finish'))
async def finish_cart(callback: CallbackQuery, session: AsyncSession):
    if callback.data.split('_')[1] == 'tayyor':
        await callback.answer()
        await callback.message.answer("✅ Hurmatli mijoz! Buyurtmangiz uchun tashakkur.")
    else:
        await callback.message.edit_text('❌ Bekor qilindi')
        await callback.message.answer('Asosiy menu', reply_markup=get_reply_keyboard(
            "📚 Kitoblar",
            "📃 Mening buyurtmalarim",
            "🔵 Biz ijtimoiy tarmoqlarda",
            "📞 Biz bilan bog'lanish",
            sizes=(1, 1, 2)
        ))


@user_private_router.message(F.text == "📞 Biz bilan bog'lanish")
async def about_us(message: Message):
    await message.answer(
        "Telegram: @RRF_0406\n\n📞 +998977090406\n\nBizning guruximiz: t.me/rrf_factor_books_group")
