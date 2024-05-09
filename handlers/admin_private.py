import requests
import aiohttp

from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from database.orm_query import orm_add_product, orm_get_categories
from filters.chat_types import ChatTypeFilter, IsAdmin
from keyboards.inline_keyboards import get_inline_keyboard
from keyboards.reply_keyboards import get_reply_keyboard

admin_private_router = Router()
admin_private_router.message.filter(ChatTypeFilter([ChatType.PRIVATE]), IsAdmin())

ADMIN_KB = get_reply_keyboard(
    "Produkt qo'shish",
    "Barcha produktlarni ko'rish",
    sizes=(2,)
)


@admin_private_router.message(Command(commands='admin'))
async def admin(message: Message):
    await message.answer('Qanday amal bajarmoxchisiz?)', reply_markup=ADMIN_KB)


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


@admin_private_router.message(F.text == "Produkt qo'shish")
async def add_product(message: Message, state: FSMContext):
    await message.answer("Product nomini kiriting: ", reply_markup=ReplyKeyboardRemove())
    await state.set_state(AddProduct.name)


@admin_private_router.message(StateFilter('*'), or_f(F.text.casefold() == 'cancel', Command(commands='cancel')))
async def cancel(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    await message.answer('Bekor qilindi!')


@admin_private_router.message(StateFilter('*'), or_f(F.text.casefold() == 'step over', Command(commands='step over')))
async def step_over(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == AddProduct.name:
        await message.answer('Siz eng boshida turipsiz!')
        return
    previous = None
    for step in AddProduct.__all_states__:
        if step == current_state:
            await state.set_state(previous)
            await message.answer(f"Siz bir qadam ortga otdingiz\n{AddProduct.texts[previous.state]}")
        previous = step


@admin_private_router.message(AddProduct.name, F.text)
async def add_product(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AddProduct.author)
    await message.answer("Product muallifini kiriting: ")


@admin_private_router.message(AddProduct.name)
async def add_product(message: Message):
    await message.answer("Product nomini to'ri kiriting: ")


@admin_private_router.message(AddProduct.author, F.text)
async def add_product_muallifi(message: Message, state: FSMContext):
    await state.update_data(author=message.text)
    await state.set_state(AddProduct.genre)
    await message.answer("Product janri kiriting: ")


@admin_private_router.message(AddProduct.author)
async def add_product_muallifi(message: Message):
    await message.answer("Product muallifini to'ri kiriting: ")


@admin_private_router.message(AddProduct.genre, F.text)
async def add_product_janri(message: Message, state: FSMContext):
    await state.update_data(genre=message.text)
    await state.set_state(AddProduct.translator)
    await message.answer("Product tarjimon kiriting: ")


@admin_private_router.message(AddProduct.genre)
async def add_product_janri(message: Message):
    await message.answer("Produkt ning janrini to'ri kiriting: ")


@admin_private_router.message(AddProduct.translator, F.text)
async def add_product_tarjimon(message: Message, state: FSMContext):
    await state.update_data(translator=message.text)
    await state.set_state(AddProduct.page)
    await message.answer("Produkt ning betlar sonini kiriting: ")


@admin_private_router.message(AddProduct.translator)
async def add_product_tarjimon(message: Message):
    await message.answer("Produkt ning tarjimonini to'ri kiriting: ")


@admin_private_router.message(AddProduct.page, F.text)
async def add_product_bet(message: Message, state: FSMContext):
    await state.update_data(page=int(message.text))
    await state.set_state(AddProduct.cover)
    await message.answer("Produkt ning muqovasini kiriting: ")


@admin_private_router.message(AddProduct.page)
async def add_product_bet(message: Message):
    await message.answer("Produkt ning betlar sonin to'ri kiriting: ")


@admin_private_router.message(AddProduct.cover, F.text)
async def add_product_muqova(message: Message, state: FSMContext, session: AsyncSession):
    await state.update_data(cover=message.text)
    categories = await orm_get_categories(session)
    btns = {category.name: str(category.id) for category in categories}
    await state.set_state(AddProduct.category)
    await message.answer("Produkt ning kategoriyasini tanlang: ", reply_markup=get_inline_keyboard(btns=btns))


@admin_private_router.message(AddProduct.cover)
async def add_product_muqova(message: Message):
    await message.answer("Produkt ning muqovasini to'ri kiriting: ")


@admin_private_router.callback_query(AddProduct.category)
async def add_product_category(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    if int(callback.data) in [category.id for category in await orm_get_categories(session)]:
        await callback.answer()
        await state.update_data(category=int(callback.data))
        await state.set_state(AddProduct.photo)
        await callback.message.answer('Produkt ning rasmini kiriting')
    else:
        await callback.message.answer('Kategoriya tanlang: ')
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
                    print(f"Error uploading file: {response.status}")
                    return None

    file = await message.bot.get_file(message.photo[-1].file_id)
    img_byte = (await message.bot.download(file.file_id)).read()
    url = await upload_file(img_byte)

    await state.update_data(photo=url)
    await state.set_state(AddProduct.price)
    await message.answer("Product narxi kiriting: ")


@admin_private_router.message(AddProduct.photo)
async def add_product_rasm(message: Message):
    await message.answer("Produkt ning rasmini to'ri kiriting: ")


@admin_private_router.message(AddProduct.price)
async def add_product_narxi(message: Message, state: FSMContext, session: AsyncSession):
    try:
        float(message.text)
        await state.update_data(price=float(message.text))
        data = await state.get_data()
        await orm_add_product(session, data)
        await message.answer("Produkt qo'shildi", reply_markup=ADMIN_KB)
        await state.clear()

    except Exception as e:
        await message.answer(f"Ooops something went wrong {e}!", reply_markup=ADMIN_KB)
        await state.clear()


@admin_private_router.message(F.text == 'Show all products')
async def show_all_products(message: Message, session: AsyncSession):
    categories = await orm_get_categories(session)
    btns = {category.name: f"category_{category.id}" for category in categories}
    await message.answer("kategoriyalardan birini tanlang: ", reply_markup=get_inline_keyboard(btns=btns))
