from sqlalchemy import Float, Text, String, DateTime, func, Column, ForeignKey, Numeric, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)


class Product(Base):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nomi: Mapped[str] = mapped_column(String(255), nullable=False)
    muallifi: Mapped[str] = mapped_column(String(255), nullable=False)
    janri: Mapped[str] = mapped_column(String(255), nullable=False)
    tarjimon: Mapped[str] = mapped_column(String(255), nullable=False)
    bet: Mapped[int] = mapped_column(nullable=False)
    muqova: Mapped[str] = mapped_column(String(255), nullable=False)
    rasmi: Mapped[str] = mapped_column(String(255), nullable=False)
    narxi: Mapped[float] = mapped_column(Numeric(6, 3), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id', ondelete='CASCADE'), nullable=False)

    category: Mapped["Category"] = relationship(backref='products')


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(unique=True)
    first_name: Mapped[str] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str] = mapped_column(String(255), nullable=True)
    phone: Mapped[str] = mapped_column(String(13), nullable=True)


class Cart(Base):
    __tablename__ = 'carts'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    quantity: Mapped[int]

    user: Mapped['User'] = relationship(backref='carts')
    product: Mapped['Product'] = relationship(backref='carts')


class Queue(Base):
    __tablename__ = 'queues'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)

    user: Mapped['User'] = relationship(backref='queue')
