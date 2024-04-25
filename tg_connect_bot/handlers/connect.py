import datetime
import re
import decouple
import aiogram.exceptions
from configuration import autoresponse

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import types, Dispatcher, F

from keyboards import inline
from database import payments, users, texts
from payments import stripe_engine
from handlers import verify_email

class Connect(StatesGroup):
    email_ = State()


async def connect_email(call: types.CallbackQuery, state: FSMContext):
    email = decouple.config('OUR_EMAIL').split("@")
    # email = ''.join([email[0], "+", str(call.from_user.id), "@", email[1]])
    number = await users.get_email_count()+300
    email = ''.join([email[0], "+", str(number), "@", email[1]])
    await users.insert_new_email(call.from_user.id, email)
    await state.set_state(Connect.email_)
    await call.message.delete()
    await state.update_data(user_email=email)
    await call.message.answer(f'''
Instruction with pictures: {decouple.config('OUR_SITE')}/instructions

Need our support? Visit: {decouple.config('OUR_SITE')}/support

1. Log in to your Yelp for Business account by visiting biz.yelp.com/login. Please ensure you use a web browser and do not log in via the Yelp iOS or Android app.

2. If prompted, click "Continue in browser." (Note: This may appear on mobile devices only.)

3. Click on the round profile icon located in the upper right corner of the page.

4. From the dropdown menu, select "Account Settings."

5. In the "Account Settings" section, locate the "User Management" line and click "Edit."

6. Click on "Invite User"

7. Enter email address from bellow (You can use Copy/Paste)

8. Click the "Save" button.

9. After completing the process, confirm by pressing "done" in the Telegram Bot and follow the instructions.


↓↓↓ USE THIS EMAIL ON STEP 7 ↓↓↓''')
    await call.message.answer(f'''{email}''', reply_markup=inline.email_done())


async def connect_email_step2(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer("Connecting to the account. This process may take up to 3 minutes...")
    email = (await state.get_data())['user_email']
    print('[connect] ', email)
    verified = await verify_email.verify_email(email)
#    verified=True
    if not verified:
        await state.clear()
        await call.message.answer(f"Something went wrong, please, start over.", reply_markup=inline.new_user())
    else:
        print(verified)
        await state.clear()
        await users.insert_new_user(call.from_user.id, email, decouple.config('PASSWORD'))
        await users.new_prompt(call.from_user.id, "Please just reply exactly like that: Hello! Thank you for your "
                                                  "inquiry! We will read your message soon and respond to it")
        # await call.message.answer(f"Your account successfully saved.\n"
        #                             f"Now you need to add new prompt for creation autoresponse through ChatGPT,\n"
        #                             f"<em>f.e Please just reply exactly like that: Hello! Thank you for your inquiry! We will read your message soon and respond to it.</em> - that's prompt set by default\n\n <a {decouple.config('OUR_SITE')}/prompt'>Prompt Template.</a>",
        #                  reply_markup=inline.new_prompt())
        await call.message.answer(
                        f'''Your account has been successfully connected. 
                        
                        Now, you need to add a prompt. This prompt serves as an instruction for ChatGPT on how to respond to your customers. It should include information about your business and your preferences regarding customer responses.
                        
                        Please view an example of the prompt at this link: {decouple.config('OUR_SITE')}/prompt
                        ''',
                             reply_markup=inline.new_prompt())


async def check_transaction(call: types.CallbackQuery):
    transaction_id = None
    status, payment_url = None, None
    try:
        transaction_id = await payments.get_transaction(call.from_user.id)
        status, payment_url = stripe_engine.check_payment_status(transaction_id[0])
        # status = "complete"
    except Exception as e:
        print(f"[connect.py][check_transaction]\n {e}")
        status, payment_url = "error", 'http://127.0.0.1/'
    if status == "complete" or status == 'paid':
        await call.message.edit_text(
            "Transaction Successful! Now you can test email responses in profile "
            "by using Playground section and run autoresponse task.",
            reply_markup=inline.profile())
        date_start = datetime.datetime.now().date()
        date_end = date_start + datetime.timedelta(days=30)
        await users.activate_subscription(call.from_user.id)
        await payments.add_subscription(call.from_user.id, date_start, date_end)
        await payments.update_payment_status(call.from_user.id, status)
    else:
        try:
            await call.message.edit_text(f"Your transaction status is {status}!\n\n"
                                         "To continue connecting to our service, please pay the service fee",
                                         reply_markup=inline.get_payment_info(payment_url))
        except aiogram.exceptions.TelegramBadRequest:
            await call.message.edit_text(f"Your transaction status is still {status}!\n\n"
                                         "To continue connecting to our service, please pay the service fee",
                                         reply_markup=inline.get_payment_info(payment_url))


async def run_task(call: types.CallbackQuery):
    await call.message.delete()
    email, password, _ = await users.get_user_data(tg_id=call.from_user.id)
    _, system_prompt = await texts.get_texts()
    await users.run_task(call.from_user.id)
    await call.message.answer("Task started! You can stop it in Profile section", reply_markup=inline.profile())
    return
    # await autoresponse.run_task_api(email, password, system_prompt, call.message.text, call.from_user.id)
    await call.message.answer("Task stopped! You can run it in Profile section", reply_markup=inline.profile())
    await users.disable_task(call.from_user.id)


async def disable_task(call: types.CallbackQuery):
    await call.message.delete()
    await call.message.answer("Start the process of stopping the task.")
    await users.disable_task(call.from_user.id)
    await call.message.answer("Task stopped! You can run it in Profile section", reply_markup=inline.profile())



async def register(dp: Dispatcher):
    dp.callback_query.register(connect_email, F.data == 'connect_service')
    # dp.message.register(connect_email_step2, Connect.email_)
    dp.callback_query.register(connect_email_step2, F.data == 'connect_email_step2')
    # dp.message.register(connect_email_finish, Connect.password, flags={'long_operation': 'typing'})
    dp.callback_query.register(check_transaction, F.data == "check_payment")
    dp.callback_query.register(run_task, F.data == 'run_task')
    dp.callback_query.register(disable_task, F.data == 'stop_task')
