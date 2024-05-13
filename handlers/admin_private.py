import requests
import aiohttp

from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from database.orm_query import orm_add_product, orm_get_categories, orm_add_category, orm_get_order, orm_get_user_cart, \
    orm_get_product, orm_add_ordered_products, orm_clear_cart
from filters.chat_types import ChatTypeFilter, IsAdmin
from keyboards.inline_keyboards import get_inline_keyboard
from keyboards.reply_keyboards import get_reply_keyboard
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __

admin_private_router = Router()
admin_private_router.message.filter(ChatTypeFilter([ChatType.PRIVATE, ChatType.SUPERGROUP, ChatType.GROUP]), IsAdmin())


@admin_private_router.message(Command(commands='admin'))
async def admin(message: Message):
    await message.answer(_('Qanday amal bajarmoxchisiz?'), reply_markup=get_reply_keyboard(_("Produkt qo'shish"),
                                                                                           _("Barcha produktlarni ko'rish"),
                                                                                           _("Kategory qo'shish"),
                                                                                           _("🌐 Tilni tanlash"),
                                                                                           sizes=(2,)
                                                                                           ))

    class AddProduct(StatesGroup):
        name = State()
        author = State()
        genre = State()
        translator = State()
        page = State()
        cover = State()
        category = State()
        price = State()
        photo = State()

        texts = {
            "AddProduct.name": 'Product nomini kiriting: ',
            "AddProduct.author": 'Product author kiriting: ',
            "AddProduct.genre": 'Product genre kiriting: ',
            "AddProduct.translator": 'Product translator kiriting: ',
            "AddProduct.page": 'Product page kiriting: ',
            "AddProduct.cover": 'Product cover kiriting: ',
            "AddProduct.photo": 'Product photo kiriting: ',
            "AddProduct.price": 'Product price kiriting: '
        }

    @admin_private_router.message(F.text == __("Produkt qo'shish"))
    async def add_product(message: Message, state: FSMContext):
        await message.answer(_("Product nomini kiriting: "), reply_markup=ReplyKeyboardRemove())
        await state.set_state(AddProduct.name)

    @admin_private_router.message(StateFilter('*'), or_f(F.text.casefold() == __('cancel'), Command(commands='cancel')))
    async def cancel(message: Message, state: FSMContext):
        current_state = await state.get_state()
        if current_state is None:
            return
        await state.clear()
        await message.answer('Bekor qilindi!')
        await message.answer(text=_("Qanday amal bajarmoxchisiz?"),
                             reply_markup=get_reply_keyboard(_("Produkt qo'shish"),
                                                             _("Barcha produktlarni ko'rish"),
                                                             _("Kategory qo'shish"),
                                                             _("🌐 Tilni tanlash"),
                                                             sizes=(2,)
                                                             ))

    @admin_private_router.message(StateFilter('*'),
                                  or_f(F.text.casefold() == __('step over'), Command(commands='step over')))
    async def step_over(message: Message, state: FSMContext):
        current_state = await state.get_state()
        if current_state == AddProduct.name:
            await message.answer(_('Siz eng boshida turipsiz!'))
            return
        previous = None
        for step in AddProduct.__all_states__:
            if step == current_state:
                await state.set_state(previous)
                await message.answer(
                    _("Siz bir qadam ortga otdingiz\n{step_over}").format(step_over=AddProduct.texts[previous.state]))
            previous = step

    @admin_private_router.message(AddProduct.name, F.text)
    async def add_product(message: Message, state: FSMContext):
        await state.update_data(name=message.text)
        await state.set_state(AddProduct.author)
        await message.answer(_("Product muallifini kiriting: "))

    @admin_private_router.message(AddProduct.name)
    async def add_product(message: Message):
        await message.answer(_("Product nomini to'ri kiriting: "))

    @admin_private_router.message(AddProduct.author, F.text)
    async def add_product_muallifi(message: Message, state: FSMContext):
        await state.update_data(author=message.text)
        await state.set_state(AddProduct.genre)
        await message.answer(_("Product janri kiriting: "))

    @admin_private_router.message(AddProduct.author)
    async def add_product_muallifi(message: Message):
        await message.answer(_("Product muallifini to'ri kiriting: "))

    @admin_private_router.message(AddProduct.genre, F.text)
    async def add_product_janri(message: Message, state: FSMContext):
        await state.update_data(genre=message.text)
        await state.set_state(AddProduct.translator)
        await message.answer(_("Product tarjimon kiriting: "))

    @admin_private_router.message(AddProduct.genre)
    async def add_product_janri(message: Message):
        await message.answer(_("Produkt ning janrini to'ri kiriting: "))

    @admin_private_router.message(AddProduct.translator, F.text)
    async def add_product_tarjimon(message: Message, state: FSMContext):
        await state.update_data(translator=message.text)
        await state.set_state(AddProduct.page)
        await message.answer(_("Produkt ning betlar sonini kiriting: "))

    @admin_private_router.message(AddProduct.translator)
    async def add_product_tarjimon(message: Message):
        await message.answer(_("Produkt ning tarjimonini to'ri kiriting: "))

    @admin_private_router.message(AddProduct.page, F.text)
    async def add_product_bet(message: Message, state: FSMContext):
        await state.update_data(page=int(message.text))
        await state.set_state(AddProduct.cover)
        await message.answer(_("Produkt ning muqovasini kiriting: "))

    @admin_private_router.message(AddProduct.page)
    async def add_product_bet(message: Message):
        await message.answer(_("Produkt ning betlar sonin to'ri kiriting: "))

    @admin_private_router.message(AddProduct.cover, F.text)
    async def add_product_muqova(message: Message, state: FSMContext, session: AsyncSession):
        await state.update_data(cover=message.text)
        categories = await orm_get_categories(session)
        btns = {category.name: str(category.id) for category in categories}
        await state.set_state(AddProduct.category)
        await message.answer(_("Produkt ning kategoriyasini tanlang: "), reply_markup=get_inline_keyboard(btns=btns))

    @admin_private_router.message(AddProduct.cover)
    async def add_product_muqova(message: Message):
        await message.answer(_("Produkt ning muqovasini to'ri kiriting: "))

    @admin_private_router.callback_query(AddProduct.category)
    async def add_product_category(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
        if int(callback.data) in [category.id for category in await orm_get_categories(session)]:
            await callback.answer()
            await state.update_data(category=int(callback.data))
            await state.set_state(AddProduct.photo)
            await callback.message.answer(_('Produkt ning rasmini kiriting'))
        else:
            await callback.message.answer(_('Kategoriya tanlang: '))
            await callback.answer()

    @admin_private_router.message(AddProduct.photo, F.photo)
    async def add_product_rasm(message: Message, state: FSMContext):
        async def upload_file(img_bytes):
            url = 'https://telegra.ph/upload'
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data={'file': img_bytes}) as response:
                    if response.status == 200:
                        data = await response.json()
                        image_url = "https://telegra.ph" + data[0]['src']
                        return image_url
                    else:
                        print(_("Error uploading file: {response_status}").format(response_status=response.status))
                        return None

        file = await message.bot.get_file(message.photo[-1].file_id)
        img_byte = (await message.bot.download(file.file_id)).read()
        url = await upload_file(img_byte)

        await state.update_data(photo=url)
        await state.set_state(AddProduct.price)
        await message.answer(_("Product narxi kiriting: "))

    @admin_private_router.message(AddProduct.photo)
    async def add_product_rasm(message: Message):
        await message.answer(_("Produkt ning rasmini to'ri kiriting: "))

    @admin_private_router.message(AddProduct.price)
    async def add_product_narxi(message: Message, state: FSMContext, session: AsyncSession):
        try:
            float(message.text)
            await state.update_data(price=float(message.text))
            data = await state.get_data()
            await orm_add_product(session, data)
            await message.answer(_("Produkt qo'shildi"), reply_markup=get_reply_keyboard(_("Produkt qo'shish"),
                                                                                         _("Barcha produktlarni ko'rish"),
                                                                                         _("Kategory qo'shish"),
                                                                                         _("🌐 Tilni tanlash"),
                                                                                         sizes=(2,)
                                                                                         ))
            await state.clear()

        except Exception as e:
            await message.answer(_("Ooops something went wrong {e}!").format(e=e),
                                 reply_markup=get_reply_keyboard(_("Produkt qo'shish"),
                                                                 _("Barcha produktlarni ko'rish"),
                                                                 _("Kategory qo'shish"),
                                                                 sizes=(2,)
                                                                 ))
            await state.clear()

    @admin_private_router.message(F.text == __("Barcha produktlarni ko'rish"))
    async def show_all_products(message: Message, session: AsyncSession):
        categories = await orm_get_categories(session)
        btns = {category.name: f"category_{category.id}" for category in categories}
        await message.answer(_("Kategoriyalardan birini tanlang: "), reply_markup=get_inline_keyboard(btns=btns))

    @admin_private_router.message(F.text == __("Kategory qo'shish"))
    async def add_category(message: Message, state: FSMContext, session: AsyncSession):
        await state.set_state(AddProduct.category)
        await message.answer(_("Kategoriyani ismini kiriting: "), reply_markup=ReplyKeyboardRemove())

    @admin_private_router.message(AddProduct.category)
    async def add_category(message: Message, state: FSMContext, session: AsyncSession):
        await state.update_data(category_name=message.text)
        data = await state.get_data()
        await state.clear()
        try:
            await orm_add_category(session, category_name=data.get('category_name'))
            await message.answer(_("Kategoriya qo'shildi!"))
            await message.answer(text=_("Qanday amal bajarmoxchisiz?"),
                                 reply_markup=get_reply_keyboard(_("Produkt qo'shish"),
                                                                 _("Barcha produktlarni ko'rish"),
                                                                 _("Kategory qo'shish"),
                                                                 _("🌐 Tilni tanlash"),
                                                                 sizes=(2,)
                                                                 ))
        except Exception as e:
            await message.answer(_('Bunday kategoriya mavjud: {e}').format(e=e))


@admin_private_router.callback_query(F.data.startswith('final'))
async def admin_accept(callback: CallbackQuery, session: AsyncSession):
    await callback.answer()
    user_id = int(callback.data.split("_")[-1])
    order_number = int(callback.data.split("_")[3])
    carts = await orm_get_user_cart(session, user_id)
    state = True if callback.data.split("_")[1] == 'accept' else False
    for cart in carts:
        product = await orm_get_product(session, cart.product_id)
        await orm_add_ordered_products(session, order_number, user_id, product.id, cart.quantity, state=state)
    await orm_clear_cart(session, callback.from_user.id)
    await callback.message.delete()


