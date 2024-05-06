from aiogram import Router
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, InlineQueryResult
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import orm_get_products, orm_get_all_products_by_startswith

inline_router = Router()


@inline_router.inline_query()
async def user_inline_handler(inline_query: InlineQuery, session: AsyncSession) -> InlineQueryResult:
    if inline_query.query == "":
        products = await orm_get_products(session)
        inline_list = []
        for product in products[:50]:
            inline_list.append(InlineQueryResultArticle(
                id=str(product.id),
                title=product.nomi,
                input_message_content=InputTextMessageContent(
                    message_text=str(product.id)
                ),
                thumbnail_url="https://telegra.ph/file/8006558d9ff33ced877d2.png",
                description=str(product.narxi)
            ))

        await inline_query.answer(inline_list)
    else:
        products = await orm_get_all_products_by_startswith(session, inline_query.query)
        inline_list = []
        for product in products[:50]:
            inline_list.append(InlineQueryResultArticle(
                id=str(product.id),
                title=product.nomi,
                input_message_content=InputTextMessageContent(
                    message_text=str(product.id)
                ),
                thumbnail_url="https://telegra.ph/file/8006558d9ff33ced877d2.png",
                description=str(product.narxi)
            ))

        await inline_query.answer(inline_list)
