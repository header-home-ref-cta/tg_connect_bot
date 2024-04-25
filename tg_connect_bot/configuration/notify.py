import datetime
from decouple import config

from database import users, payments
from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError
import json


async def notify(data):
    email, letter, resp = json.loads(data.decode()).values()
    tg_id = await users.get_tg_id_by_email(email)
    bot = Bot(token=config("BOT_TOKEN"), parse_mode='html')
    session = bot.session
    try:
        await bot.send_message(chat_id=tg_id,
                               text=f"<b>Successfully send message to lead!\nLoad details:</b>\n{letter}\n" 
                                    f"<b>Answer:</b>\n"
                                    f"{resp}")
    except TelegramForbiddenError:
        print(f"[notify] There is some troubles with Telegram ID {tg_id}")

    await session.close()
