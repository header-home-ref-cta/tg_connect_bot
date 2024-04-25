import decouple

from aiogram import Bot
from aiogram.types import BotCommand

from handlers.commands import register as reg_handlers
from handlers.admin import register as reg_admin
from handlers.connect import register as reg_connect
from handlers.profile import register as reg_profile
from middlewares.chat_action import ChatActionMiddleware, ChatActionMiddlewareCall
# from handlers.seledka import browser_handler_headless as start_browser_headless
# from handlers.seledka import browser_handler as start_browser

bot = Bot(token=decouple.config('BOT_TOKEN'), parse_mode='html')
admin_ids = [int(id_str) for id_str in decouple.config("ADMIN_IDS").split(',')]


async def bot_commands():
    await bot.set_my_commands(
        [
            BotCommand(command='start', description='Bot Start'),
            BotCommand(command='info', description='Bot Info')
        ]
    )


async def register_handlers(dp):
    await reg_handlers(dp)
    await reg_admin(dp)
    await reg_connect(dp)
    await reg_profile(dp)
    # await start_browser()
    # await start_browser_headless()


async def register_middlewares(dp):
    dp.message.middleware.register(ChatActionMiddleware())
    dp.callback_query.middleware.register(ChatActionMiddlewareCall())
