from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from common.text_for_database import categories
from config import DB_URL
from database.models import Base
from database.orm_query import orm_create_categories

engine = create_async_engine(DB_URL, echo=True)

session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_maker() as session:
        await orm_create_categories(session, categories)


async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
