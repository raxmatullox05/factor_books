from aiogram import Router

from handlers.admin_private import admin_private_router
from handlers.user_private import user_private_router
from handlers.user_group import user_group_router
from handlers.user_private_inline import inline_router

start_router = Router()
start_router.include_routers(
    user_group_router,
    admin_private_router,
    user_private_router,
    inline_router
)
