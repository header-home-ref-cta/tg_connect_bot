from configuration import settings, autoresponse

from aiogram import types, Dispatcher, F
from aiogram.filters import Command, CommandObject

from database import users, texts
from keyboards import inline
from payments import stripe_engine
from database import payments
import decouple


async def get_file_id(msg: types.Message):
    if msg.video:
        await msg.answer(msg.video.file_id)


async def start(msg: types.Message, command: CommandObject):
    if command.args:
        if command.args == "cancel":
            await msg.answer("Transaction canceled!")
        elif command.args.startswith("success"):
            args = command.args.split("_")[1]
            transaction_id = await payments.get_transaction(msg.from_user.id)
            status, _ = stripe_engine.check_payment_status(transaction_id[0])

            # if args == msg.from_user.id and (status == 'complete' or status == 'paid'):
            if (status == 'complete' or status == 'paid'):
                await users.activate_subscription(msg.from_user.id)
                await msg.answer("Transaction complete and task started!", reply_markup=inline.profile())
                await payments.update_payment_status(msg.from_user.id, status)
                await users.run_task(msg.from_user.id,)
    else:
        all_users = await users.all_users()
        if msg.from_user.id not in all_users:
            text = (f"Hello, {msg.from_user.first_name}! We use the most advanced OpenAI chatbot to assist you in "
                    f"closing more deals with clients on Yelp Biz. Connect our bot, and it will automatically send "
                    f"intelligent responses with a call to action to your clients' inquiries. For more information, "
                    f"please visit our website at <a href='{decouple.config('OUR_SITE')}/'>ConnectTo.Chat.</a>")
            await msg.answer(text, reply_markup=inline.new_user())
        else:
            subscription_status = await users.check_subscription(msg.from_user.id)
            if subscription_status == 0:
                new_link, _ = stripe_engine.create_payment_link(msg.from_user.id)
                text = 'Hello, you have unfinished payment. You can check status of previous payment in Profile or ' \
                       'try again\n'
                text += decouple.config('PROP')
                # await msg.answer("Task stopped. If you subscription is over, you need to pay again for continue using our "
                #              "autoresponse service, if you have active subscription, but anyway seeing that message, "
                #              "you need to connect with our customer service.")
                if len(await users.all_users_subs()) > 14:
                    await msg.answer('Sorry, I only serve 10 users.')
                else:
                    await msg.answer(text, reply_markup=inline.profile())
            else:
                text = (f"Hello, {msg.from_user.first_name}! We are delighted that you are using our product. We "
                        f"employ the most advanced chatbot from OpenAI to help you close more deals with clients. "
                        f"Please feel free to reach out with any questions. You can find our contact information on "
                        f"the <a href='{decouple.config('OUR_SITE')}/'>ConnectTo.Chat</a> website.\n\n"
                        f"If you would like to modify the responses from the bot, please update the prompt ("
                        f"instructions for the bot) in your profile.")
                await msg.answer(text, reply_markup=inline.profile())


async def info(msg: types.Message):
    info_text, _ = await texts.get_texts()
    await msg.answer(info_text)


async def admin(msg: types.Message):
    if msg.from_user.id in settings.admin_ids:
        await msg.answer('Select Option:', reply_markup=inline.admin())
    else:
        await msg.answer("Command not available")


async def clear_log_file(msg: types.Message):
    if msg.from_user.id in settings.admin_ids:
        file_path = 'logs.log'
        try:
            with open(file_path, 'w') as log_file:
                log_file.truncate(0)
            await msg.answer(f'{file_path} now clear')
        except Exception as e:
            await msg.answer(f'Error while cleaning {file_path}: {e}')


async def register(dp: Dispatcher):
    dp.message.register(get_file_id, F.video)
    dp.message.register(start, Command('start'), flags=({'long_operation': 'typing'}))
    dp.message.register(info, Command('info'))
    dp.message.register(admin, Command('admin'))
    dp.message.register(clear_log_file, Command('clear'))
