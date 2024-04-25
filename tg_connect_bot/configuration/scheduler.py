import datetime
from decouple import config

from database import users, payments
from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError


async def check_users_payments():
    print(f'Start job at: {datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}')
    all_users_ids = await users.all_users()
    for tg_id in all_users_ids:
        date_end = await payments.get_subscription_end_date(tg_id)
        if date_end:
            if date_end[0] == str(datetime.datetime.now().date() + datetime.timedelta(days=30)):
                bot = Bot(token=config("BOT_TOKEN"), parse_mode='html')
                session = bot.session
                await users.deactivate_subscription(tg_id)
                print(f"Successfully deactivate subscription to user with Telegram ID {tg_id}")
                try:
                    await bot.send_message(chat_id=tg_id,
                                           text="Your subscription is over!"
                                                "\n\nIf you liked using our service, "
                                                "you can renew your subscription by pressing the /start command!")
                except TelegramForbiddenError:
                    print(f"There is some troubles with Telegram ID {tg_id}")

                await session.close()
            else:
                pass
