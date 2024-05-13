from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Product, Category, User, Cart, Order, OrderedProduct


#################################### Products #########################################
async def orm_add_product(session: AsyncSession, data):
    obj = Product(
        name=data['name'],
        author=data['author'],
        genre=data['genre'],
        translator=data['translator'],
        page=data['page'],
        cover=data['cover'],
        category_id=data['category'],
        photo=data['photo'],
        price=data['price']
    )

    session.add(obj)
    await session.commit()


async def orm_get_product(session: AsyncSession, product_id: int):
    query = select(Product).where(Product.id == product_id)
    result = await session.execute(query)
    return result.scalar()


async def orm_get_products(session: AsyncSession, category_id: int = None):
    if category_id:
        query = select(Product).where(Product.category_id == category_id)
        result = await session.execute(query)
        return result.scalars().all()
    else:
        query = select(Product)
        result = await session.execute(query)
        return result.scalars().all()


async def orm_get_all_products_by_startswith(session: AsyncSession, startswith: str):
    query = select(Product).where(Product.name.ilike(f'%{startswith}%'))
    result = await session.execute(query)
    return result.scalars().all()


async def orm_update_product(session: AsyncSession, product_id: int, **data: dict[str, str]):
    query = update(Product).where(Product.id == product_id).values(data)
    await session.execute(query)
    await session.commit()


async def orm_delete_product(session: AsyncSession, product_id: int):
    query = delete(Product).where(Product.id == product_id)
    await session.execute(query)
    await session.commit()


################################## Categories ################################

async def orm_create_categories(session: AsyncSession, categories: list):
    query = select(Category)
    result = await session.execute(query)
    if result.first():
        return
    session.add_all([Category(name=name) for name in categories])
    await session.commit()


async def orm_get_categories(session: AsyncSession):
    query = select(Category)
    result = await session.execute(query)
    return result.scalars()


async def orm_get_category(session: AsyncSession, category_id: int):
    query = select(Category).where(Category.id == category_id)
    result = await session.execute(query)
    return result.scalar()


####################################### Users #####################################
async def orm_add_user(session: AsyncSession,
                       user_id: int,
                       first_name: str | None = None,
                       last_name: str | None = None,
                       phone: str | None = None
                       ):
    query = select(User).where(User.user_id == user_id)
    result = await session.execute(query)
    if result.first() is None:
        session.add(
            User(user_id=user_id, first_name=first_name, last_name=last_name, phone=phone)
        )
        await session.commit()


async def orm_update_user(session: AsyncSession, user_id: int, **data: dict[str, str]):
    query = update(User).where(User.user_id == user_id).values(data)
    await session.execute(query)
    await session.commit()


######################################### Basket ###################################


async def orm_add_to_cart(session: AsyncSession, user_id: int, product_id: int, amount: int = 1):
    query = select(Cart).where(Cart.user_id == user_id, Cart.product_id == product_id)
    cart = await session.execute(query)
    cart = cart.scalar()
    if cart:
        cart.quantity += amount
        await session.commit()
        return cart
    else:
        session.add(Cart(user_id=user_id, product_id=product_id, quantity=amount))
        await session.commit()


async def orm_get_user_cart(session: AsyncSession, user_id: int):
    query = select(Cart).where(Cart.user_id == user_id)
    result = await session.execute(query)
    result = result.scalars().all()
    return result


async def orm_clear_cart(session: AsyncSession, user_id: int):
    query = delete(Cart).where(Cart.user_id == user_id)
    await session.execute(query)
    await session.commit()


######################################### Queue ######################################

async def orm_set_order(session: AsyncSession, user_id: int):
    query = select(Order).where(Order.user_id == user_id)
    result = await session.execute(query)
    if result.first() is None:
        session.add(Order(user_id=user_id))
        await session.commit()


async def orm_get_order(session, user_id: int):
    query = select(Order).where(Order.user_id == user_id)
    result = await session.execute(query)
    result = result.scalar()
    return result


async def orm_get_orders(session, user_id: int):
    query = select(Order).where(Order.user_id == user_id)
    result = await session.execute(query)
    result = result.scalars().all()
    return result


async def orm_add_ordered_products(session: AsyncSession, order_id,
                                   user_id: int,
                                   product_id: int,
                                   cart_quantity: int,
                                   state: bool = False
                                   ):
    obj = OrderedProduct(
        order_number=order_id,
        user_id=user_id,
        product_id=product_id,
        cart_quantity=cart_quantity,
        state=state
    )
    session.add(obj)
    await session.commit()


async def orm_get_ordered_products(session: AsyncSession, user_id: int):
    query = select(OrderedProduct).where(OrderedProduct.user_id == user_id)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_add_category(session: AsyncSession,
                           category_name: str):
    session.add(Category(name=category_name))
    await session.commit()
