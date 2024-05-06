import requests

from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.filters import CommandStart, Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import orm_add_product, orm_get_categories, orm_create_categories, orm_get_products, \
    orm_get_product, orm_get_category
from filters.chat_types import ChatTypeFilter, IsAdmin
from keyboards.inline_keyboards import get_inline_keyboard
from keyboards.reply_keyboards import get_reply_keyboard

admin_private_router = Router()
admin_private_router.message.filter(ChatTypeFilter([ChatType.PRIVATE]), IsAdmin())

ADMIN_KB = get_reply_keyboard(
    "Add a product",
    "Show all products",
    sizes=(2,)
)


@admin_private_router.message(Command(commands='admin'))
async def admin(message: Message):
    await message.answer('What do you want to do?', reply_markup=ADMIN_KB)


class AddProduct(StatesGroup):
    nomi = State()
    muallifi = State()
    janri = State()
    tarjimon = State()
    bet = State()
    muqova = State()
    category = State()
    narxi = State()
    rasm = State()

    texts = {
        "AddProduct:nomi": 'Product nomini kiriting: ',
        "AddProduct:muallifi": 'Product muallifi kiriting: ',
        "AddProduct:janri": 'Product janri kiriting: ',
        "AddProduct:tarjimon": 'Product tarjimon kiriting: ',
        "AddProduct:bet": 'Product bet kiriting: ',
        "AddProduct:muqova": 'Product muqova kiriting: ',
        "AddProduct:kitob_haqida": 'Product kitob_haqida kiriting: ',
        "AddProduct:narxi": 'Product narxini kiriting: ',
    }


@admin_private_router.message(F.text == "Add a product")
async def add_product(message: Message, state: FSMContext):
    await message.answer("Product nomini kiriting: ", reply_markup=ReplyKeyboardRemove())
    await state.set_state(AddProduct.nomi)


@admin_private_router.message(StateFilter('*'), or_f(F.text.casefold() == 'cancel', Command(commands='cancel')))
async def cancel(message: Message, state: FSMContext):
    current_state = state.get_state()
    if current_state is None:
        return
    await state.clear()
    await message.answer('Rad qilindi!')


@admin_private_router.message(StateFilter('*'), or_f(F.text.casefold() == 'step over', Command(commands='step over')))
async def step_over(message: Message, state: FSMContext):
    current_state = state.get_state()
    if current_state == AddProduct.nomi:
        await message.answer('Siz end boshida turipsiz!')
        return
    previous = None
    for step in AddProduct.__all_states__:
        if step == current_state:
            await state.set_state(previous)
            await message.answer(f'Siz bir qadam ortga otdingiz\n{AddProduct.texts[previous.state]}')
        previous = step


@admin_private_router.message(AddProduct.nomi, F.text)
async def add_product(message: Message, state: FSMContext):
    await state.update_data(nomi=message.text)
    await state.set_state(AddProduct.muallifi)
    await message.answer("Product muallifini kiriting: ")


@admin_private_router.message(AddProduct.nomi)
async def add_product(message: Message):
    await message.answer("Product nomini to'ri kiriting: ")


@admin_private_router.message(AddProduct.muallifi, F.text)
async def add_product_muallifi(message: Message, state: FSMContext):
    await state.update_data(muallifi=message.text)
    await state.set_state(AddProduct.janri)
    await message.answer("Product janri kiriting: ")


@admin_private_router.message(AddProduct.muallifi)
async def add_product_muallifi(message: Message):
    await message.answer("Product muallifini to'ri kiriting: ")


@admin_private_router.message(AddProduct.janri, F.text)
async def add_product_janri(message: Message, state: FSMContext):
    await state.update_data(janri=message.text)
    await state.set_state(AddProduct.tarjimon)
    await message.answer("Product tarjimon kiriting: ")


@admin_private_router.message(AddProduct.janri)
async def add_product_janri(message: Message):
    await message.answer("Product janrini to'ri kiriting: ")


@admin_private_router.message(AddProduct.tarjimon, F.text)
async def add_product_tarjimon(message: Message, state: FSMContext):
    await state.update_data(tarjimon=message.text)
    await state.set_state(AddProduct.bet)
    await message.answer("Product bet kiriting: ")


@admin_private_router.message(AddProduct.tarjimon)
async def add_product_tarjimon(message: Message):
    await message.answer("Product tarjimonini to'ri kiriting: ")


@admin_private_router.message(AddProduct.bet, F.text)
async def add_product_bet(message: Message, state: FSMContext):
    await state.update_data(bet=int(message.text))
    await state.set_state(AddProduct.muqova)
    await message.answer("Product muqova kiriting: ")


@admin_private_router.message(AddProduct.bet)
async def add_product_bet(message: Message):
    await message.answer("Product betini to'ri kiriting: ")


@admin_private_router.message(AddProduct.muqova, F.text)
async def add_product_muqova(message: Message, state: FSMContext, session: AsyncSession):
    await state.update_data(muqova=message.text)
    categories = await orm_get_categories(session)
    btns = {category.name: str(category.id) for category in categories}
    await state.set_state(AddProduct.category)
    await message.answer("Product category sini tanlang: ", reply_markup=get_inline_keyboard(btns=btns))


@admin_private_router.message(AddProduct.muqova)
async def add_product_muqova(message: Message):
    await message.answer("Product betini to'ri kiriting: ")


@admin_private_router.callback_query(AddProduct.category)
async def add_product_category(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    if int(callback.data) in [category.id for category in await orm_get_categories(session)]:
        await callback.answer()
        await state.update_data(category=int(callback.data))
        await state.set_state(AddProduct.rasm)
        await callback.message.answer('Product rasmini kiriting')
    else:
        await callback.message.answer('Category tanlang: ')
        await callback.answer()


@admin_private_router.message(AddProduct.rasm, F.photo)
async def add_product_rasm(message: Message, state: FSMContext):
    response = requests.post('https://telegra.ph/upload', files={'file': message.photo[-1].file_id})
    print(response.status_code)
    data = response.json()
    url = "https://telegra.ph" + data[0].get('src').replace(r"\\", '')
    print(url)
    await state.update_data(rasm=url)
    await state.set_state(AddProduct.narxi)
    await message.answer("Product narxi kiriting: ")


@admin_private_router.message(AddProduct.rasm)
async def add_product_rasm(message: Message):
    await message.answer("Product rasm to'ri kiriting: ")


@admin_private_router.message(AddProduct.narxi)
async def add_product_narxi(message: Message, state: FSMContext, session: AsyncSession):
    try:
        float(message.text)
        await state.update_data(narxi=float(message.text))
        data = await state.get_data()
        await orm_add_product(session, data)
        await message.answer("Product qo'shildi", reply_markup=ADMIN_KB)
        await state.clear()

    except Exception as e:
        await message.answer(f"Ooops something went wrong {e}!", reply_markup=ADMIN_KB)
        await state.clear()


@admin_private_router.message(F.text == 'Show all products')
async def show_all_products(message: Message, session: AsyncSession):
    categories = await orm_get_categories(session)
    btns = {category.name: f"category_{category.id}" for category in categories}
    await message.answer("kategoriyalardan birini tanlang: ", reply_markup=get_inline_keyboard(btns=btns))
