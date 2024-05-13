from aiogram import Router, F, Bot
from aiogram.enums import ChatType
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, ReplyKeyboardRemove, BotCommand
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __

from database.orm_query import orm_get_categories, orm_get_category, orm_get_products, orm_get_product, orm_add_user, \
    orm_add_to_cart, orm_get_user_cart, orm_clear_cart, orm_set_order, orm_get_order, orm_get_orders, \
    orm_add_ordered_products, orm_get_ordered_products
from filters.chat_types import ChatTypeFilter
from keyboards.inline_keyboards import get_inline_keyboard
from keyboards.reply_keyboards import get_reply_keyboard

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter([ChatType.PRIVATE]))


@user_private_router.message(CommandStart())
async def start(message: Message):
    await message.answer(text=_('Assalomu alaykum {name}! Tanlang.').format(name=message.from_user.full_name),
                         reply_markup=get_reply_keyboard(
                             _("📚 Kitoblar"),
                             _("📃 Mening buyurtmalarim"),
                             _("🔵 Biz ijtimoiy tarmoqlarda"),
                             _("📞 Biz bilan bog'lanish"),
                             _("🌐 Tilni tanlash"),
                             sizes=(1, 1, 2)
                         ))


@user_private_router.message(F.text == __("📚 Kitoblar"))
async def books_fun(message: Message, session: AsyncSession):
    categories = await orm_get_categories(session)
    btns = {category.name: f"category_{category.id}" for category in categories}
    btns[_('🔍 Qidirish')] = "switch_inline_query_current_chat"
    cart = await orm_get_user_cart(session, message.from_user.id)
    if cart:
        btns[_('🛒 Savat({len})').format(len=len(cart))] = f"savat_{message.from_user.id}"
    await message.answer(_("Qaysi categoriyalarni product larini ko'rmoxchisiz: "),
                         reply_markup=get_inline_keyboard(btns=btns))


@user_private_router.message(F.text == __("🌐 Tilni tanlash"))
async def choose_language_fun(message: Message):
    await message.answer(_('Tanlang: '),
                         reply_markup=get_inline_keyboard(btns={
                             "Uz 🇺🇿": 'lang_uz',
                             "En 🇬🇧": 'lang_en'
                         }))


@user_private_router.callback_query(F.data.startswith('lang'))
async def choose_one_language(callback: CallbackQuery, state: FSMContext, bot: Bot):
    language_code = callback.data.split('_')[-1]
    language = (_("Uzbek", locale='uz'), _("Ingliz", locale='en'))[language_code == 'en']
    await state.update_data(locale=language_code)
    await bot.delete_my_commands()
    await bot.set_my_commands([
        BotCommand(command='start', description=_('🚀 Botni ishga tushirish ', locale=language_code)),
        BotCommand(command='help', description=_('⚙ Yordam kerakmi?', locale=language_code))
    ])
    await callback.answer(_("{language} tili tanlandi!", locale=language_code).format(language=language))
    await callback.message.answer(text=_('Tanlang.'),
                                  reply_markup=get_reply_keyboard(
                                      _("📚 Kitoblar", locale=language_code),
                                      _("📃 Mening buyurtmalarim", locale=language_code),
                                      _("🔵 Biz ijtimoiy tarmoqlarda", locale=language_code),
                                      _("📞 Biz bilan bog'lanish", locale=language_code),
                                      _("🌐 Tilni tanlash", locale=language_code),
                                      sizes=(1, 1, 2)
                                  ))


@user_private_router.callback_query(F.data == 'back')
async def back(callback: CallbackQuery, session: AsyncSession):
    await callback.answer()
    categories = await orm_get_categories(session)
    btns = {category.name: f"category_{category.id}" for category in categories}
    btns[_('🔍 Qidirish')] = "switch_inline_query_current_chat"
    cart = await orm_get_user_cart(session, callback.from_user.id)
    if cart:
        btns[_('🛒 Savat({len})').format(len=len(cart))] = f"basket_{callback.from_user.id}"
    await callback.message.edit_text("Kategoriyalardan birini tanlang: ",
                                     reply_markup=get_inline_keyboard(btns=btns))


@user_private_router.callback_query(F.data == 'backback')
async def backback(callback: CallbackQuery, session: AsyncSession):
    await callback.answer()
    await callback.message.delete()
    await books_fun(callback.message, session)


@user_private_router.callback_query(F.data.startswith('category_'))
async def show_products_of_category(callback: CallbackQuery, session: AsyncSession):
    category_id = int(callback.data.split('_')[-1])
    category = await orm_get_category(session, category_id)
    products = await orm_get_products(session, category.id)
    btns = {product.name: f"product_{product.id}" for product in products}
    btns[_('⬅ Orqaga')] = 'back'
    await callback.message.edit_text(f"{category.name}", reply_markup=get_inline_keyboard(btns=btns))


async def make_plus_minus(product_id, session: AsyncSession, amount: int = 1):
    product = await orm_get_product(session, int(product_id))
    if amount < 1:
        amount = 1
    reply_markup = get_inline_keyboard(btns={
        "➖": f"op_minus_{product.id}_{amount}",
        f"{amount}": f"current{amount}",
        "➕": f"op_plus_{product.id}_{amount}",
        "⬅ Orqaga": "backback",
        _("🛒 Savatga qo'shish"): f"basket_{product.id}_{amount}"
    }, sizes=(3, 2))
    return reply_markup


@user_private_router.callback_query(F.data.startswith('product_'))
async def show_product_of_category(callback: CallbackQuery, session: AsyncSession):
    product_id = callback.data.split('_')[-1]
    product = await orm_get_product(session, int(product_id))
    photo = product.photo
    caption = (
        _("""🔷 Nomi: {name}\nMuallifi: {author}\nJanri: {genre}\nTarjimon: {translator}\nBet: {page}\nMuqova: {cover}\n💸 Narxi: {price} so'm""").format(
            name=product.name, author=product.author, genre=product.genre, translator=product.translator,
            page=product.page,
            cover=product.cover, price=product.price))
    await callback.message.answer_photo(photo=photo, caption=caption,
                                        reply_markup=await make_plus_minus(product_id, session))
    await callback.message.delete()


@user_private_router.callback_query(F.data.startswith('op'))
async def operations(callback: CallbackQuery, session: AsyncSession):
    product_id = int(callback.data.split('_')[2])
    operation = callback.data.split('_')[1]
    amount = int(callback.data.split('_')[-1])
    product = await orm_get_product(session, product_id)
    photo = product.photo
    caption = (
        _("""🔷 Nomi: {name}\nMuallifi: {author}\nJanri: {genre}\nTarjimon: {translator}\nBet: {page}\nMuqova: {cover}\n💸 Narxi: {price} so'm""").format(
            name=product.name, author=product.author, genre=product.genre, translator=product.translator,
            page=product.page,
            cover=product.cover, price=product.price))
    media = InputMediaPhoto(media=photo, caption=caption)

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

    product_id = int(callback.data.split('_')[1])
    amount = int(callback.data.split("_")[-1])
    await orm_add_to_cart(session, user.id, product_id, amount)
    await callback.answer(_("Product qo'shildi"), show_alert=True)
    await callback.message.delete()
    categories = await orm_get_categories(session)
    btns = {category.name: f"category_{category.id}" for category in categories}
    btns[_('🔍 Qidirish')] = "switch_inline_query_current_chat"
    cart = await orm_get_user_cart(session, callback.from_user.id)
    if cart:
        btns[_('🛒 Savat({len})').format(len=len(cart))] = f"savat_{callback.from_user.id}"
    await callback.message.answer(_("Qaysi categoriyalarni product larini ko'rmoxchisiz: "),
                                  reply_markup=get_inline_keyboard(btns=btns))


@user_private_router.callback_query(F.data.startswith('savat'))
async def savat_info(callback: CallbackQuery, session: AsyncSession):
    user_id = int(callback.data.split('_')[-1])
    carts = await orm_get_user_cart(session, user_id)
    if carts:
        msg = _("🛒 Savat\n\n")
        summa = 0
        for i, cart in enumerate(carts, start=1):
            product = await orm_get_product(session, cart.product_id)
            msg += ("{i}. {name}\n{quantity} x {price} = {summa} so'm\n\n").format(
                i=i, name=product.name, quantity=cart.quantity, price=product.price, summa=cart.quantity * product.price
            )
            summa += cart.quantity * product.price
        msg += _("Jami: {summa} so'm").format(summa=summa)

    await callback.message.edit_text(msg, reply_markup=get_inline_keyboard(btns={
        _("❌ Savatni tozalash"): f"cart_tozalash_{user_id}",
        _("✅ Buyurtmani tasdiqlash"): f"cart_tasdiqlash_{user_id}",
        _("⬅ Orqaga"): "back"
    }, sizes=(1,)))


@user_private_router.callback_query(F.data.startswith('cart'))
async def savat_operations(callback: CallbackQuery, session: AsyncSession):
    user_id = callback.data.split('_')[-1]
    if callback.data.split('_')[1] == 'tozalash':
        await callback.answer()
        await orm_clear_cart(session, int(user_id))
        await back(callback, session)
    else:
        await callback.answer()
        await callback.message.answer(_('📞 Telefon raqam tugmasini bosing 🔽:'),
                                      reply_markup=get_reply_keyboard(_('📞 Telefon raqam'), request_contact=0))


@user_private_router.message(F.contact)
async def add_contact_to_user(message: Message, session: AsyncSession):
    user_id = message.from_user.id
    carts = await orm_get_user_cart(session, user_id)
    if carts:
        msg = _("🛒 Savat\n\n")
        summa = 0
        for i, cart in enumerate(carts, start=1):
            product = await orm_get_product(session, cart.product_id)
            msg += ("{i}. {name}\n{quantity} x {price} = {summa} so'm\n\n").format(
                i=i, name=product.name, quantity=cart.quantity, price=product.price, summa=cart.quantity * product.price
            )
            summa += cart.quantity * product.price
        msg += (_("Jami: {summa} so'm\nTelfon raqamingiz: {phone_number}\n\nBuyurtma berasizmi?").
                format(summa=summa, phone_number=message.contact.phone_number))

    await message.answer(msg, reply_markup=get_inline_keyboard(btns={
        _("❌ Yo'q"): f"finish_bekor_{user_id}",
        _("✅ Ha"): f"finish_tayyor_{user_id}",
        _("⬅ Orqaga"): "back"
    }, sizes=(1,)))


@user_private_router.callback_query(F.data.startswith('finish'))
async def finish_cart(callback: CallbackQuery, session: AsyncSession, bot: Bot):
    if callback.data.split('_')[1] == 'tayyor':
        await callback.answer()
        await callback.message.delete()
        await callback.message.answer(_("✅ Hurmatli mijoz! Buyurtmangiz uchun tashakkur."))
        await orm_set_order(session, callback.from_user.id)
        result = await orm_get_order(session, callback.from_user.id)
        await callback.message.answer(_('Buyurtma raqami: {order_number}').format(order_number=result.id))
        carts = await orm_get_user_cart(session, callback.from_user.id)
        if carts:
            msg = _("🛒 Savat\n\nBuyurtma raqami: {order_id}").format(order_id=result.id)
            summa = 0
            for i, cart in enumerate(carts, start=1):
                product = await orm_get_product(session, cart.product_id)
                msg += ("{i}. {name}\n{quantity} x {price} = {summa} so'm\n\n").format(
                    i=i, name=product.name, quantity=cart.quantity, price=product.price,
                    summa=cart.quantity * product.price
                )
                summa += cart.quantity * product.price
            msg += (_("Jami: {summa} so'm\n").
                    format(summa=summa))
            await bot.send_message(-1002006001626, msg, reply_markup=get_inline_keyboard(btns={
                _("Accept"): f"final_accept_product_{result.id}_{callback.from_user.id}",
                _("Cancel"): f"final_reject_product_{result.id}_{callback.from_user.id}",
            }))
        await callback.message.answer(_('Asosiy menu'),
                                      reply_markup=get_reply_keyboard(
                                          _("📚 Kitoblar"),
                                          _("📃 Mening buyurtmalarim"),
                                          _("🔵 Biz ijtimoiy tarmoqlarda"),
                                          _("📞 Biz bilan bog'lanish"),
                                          _("🌐 Tilni tanlash"),
                                          sizes=(1, 1, 2)
                                      ))


    else:
        await callback.message.edit_text(_('❌ Bekor qilindi'))
        await callback.message.answer(_('Asosiy menu'), reply_markup=get_reply_keyboard(
            _("📚 Kitoblar"),
            _("📃 Mening buyurtmalarim"),
            _("🔵 Biz ijtimoiy tarmoqlarda"),
            _("📞 Biz bilan bog'lanish"),
            _("🌐 Tilni tanlash"),
            sizes=(1, 1, 2)
        ))


@user_private_router.message(F.text == __("📞 Biz bilan bog'lanish"))
async def about_us(message: Message):
    await message.answer(
        _("Telegram: @RRF_0406\n\n📞 +998977090406\n\nBizning guruximiz: t.me/rrf_factor_books_group")
    )


@user_private_router.message(F.text.startswith("inline_query"))
async def inline_query_response(message: Message, session: AsyncSession):
    product_id = message.text.split("_")[-1]
    product = await orm_get_product(session, int(product_id))
    photo = product.photo
    caption = (
        _("""🔷 Nomi: {name}\nMuallifi: {author}\nJanri: {genre}\nTarjimon: {translator}\nBet: {page}\nMuqova: {cover}\n💸 Narxi: {price} so'm""").format(
            name=product.name, author=product.author, genre=product.genre, translator=product.translator,
            page=product.page,
            cover=product.cover, price=product.price))
    await message.answer_photo(photo=photo, caption=caption,
                               reply_markup=await make_plus_minus(product_id, session))
    await message.delete()


@user_private_router.message(F.text == __("📃 Mening buyurtmalarim"))
async def mening_buyurtmalarim(message: Message, session: AsyncSession):
    ordered_products = await orm_get_ordered_products(session, message.from_user.id)
    if ordered_products:
        for i, order in enumerate(ordered_products, start=1):
            if order.state is True:
                product = await orm_get_product(session, order.product_id)
                text = _(
                    """🔢 Buyurtma raqami: {order_number}\n📆 Buyurtma qilingan sana: {date}\n\n{i}. 📕 Kitob nomi: {book_name}\n{quantity} x {price} = {summa}""").format(
                    order_number=order.order_number, date=order.created, i=i, book_name=product.name,
                    quantity=order.cart_quantity,
                    price=product.price, summa=order.cart_quantity * product.price)
                await message.answer(text)
    else:
        await message.answer(_("🤷 Siz oldin buyurtma bermagansiz!"))
