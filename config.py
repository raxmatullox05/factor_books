import os

from dotenv import load_dotenv
from aiogram import Router

from handlers.admin_private import admin_private_router
from handlers.user_private import user_private_router
from handlers.user_group import user_group_router
from handlers.user_private_inline import inline_router

load_dotenv('.env')

TOKEN = os.getenv('TOKEN')
DB_URL = os.getenv('DB_URL')

# =============================== All routers ===============================

start_router = Router()
start_router.include_routers(
    admin_private_router,
    user_private_router,
    user_group_router,
    inline_router
)
