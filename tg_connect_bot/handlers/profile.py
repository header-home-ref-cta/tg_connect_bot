from aiogram import types, Dispatcher, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

import gpt.openai_engine
from payments import stripe_engine
from database import users, texts, payments
from keyboards import inline
import decouple


class Prompt(StatesGroup):
    new_prompt = State()


class ChangePrompt(StatesGroup):
    new_prompt = State()


class Playground(StatesGroup):
    details = State()


async def handle_profile(call: types.CallbackQuery):
    email, app_password, subscription = await users.get_user_data(call.from_user.id)
    subscription_end_date = await payments.get_subscription_end_date(call.from_user.id)
    # masked_password = '*' * (len(app_password) - 3) + app_password[-3:] if len(app_password) > 3 else '*' * len(
    #     app_password)
    subscription_status = 'Active' if subscription == 1 else "Not subscribed"
    subscription_end_date = f'(ends {subscription_end_date[0]})' if subscription_end_date else ' (Please use “Payment” button to subscribe)'
    task_status = await users.task_status(call.from_user.id)
    task_status_text = 'Launched' if task_status[0] == 1 else 'Stopped'
    await call.message.edit_text(
        f"<b>Email</b>: {email}"
        # f"\n<b>Password:</b> {masked_password}"
        f"\n<b>Subscription status:</b> {subscription_status} {subscription_end_date}"
        f'\n<b>Task status: {task_status_text}</b>',
        reply_markup=inline.in_profile(subscription_status, task_status, decouple.config('LINK_CUSTOMER_PORTAL')))


async def insert_new_prompt(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("Send me new prompt:")
    await state.set_state(Prompt.new_prompt)


async def save_new_prompt(msg: types.Message, state: FSMContext):
    payment_url, payment_id = stripe_engine.create_payment_link(msg.from_user.id)
    status, _ = stripe_engine.check_payment_status(payment_id)
    await payments.create_new_payment(msg.from_user.id, payment_id, status)
    await users.new_prompt(msg.from_user.id, msg.text)
    if len(await users.all_users_subs()) > 14:
        await msg.answer("New prompt successfully saved! You can change it later in Profile section.\n\n" +
                         'Sorry, I only serve 10 users.')
    else:
        # await msg.answer("New prompt successfully saved! You can change it later in Profile section.\n\n" +
        #                  "For use our service, you need pay service fee. \n" +
        #                  decouple.config('PROP'),
        #                  reply_markup=inline.get_payment_info(payment_url))

        await msg.answer('''You can try our service for free for 7 days. To activate your free trial, please click the "Payment" button to link your bank card. You can cancel your subscription at any time.\n\n''' +
                         decouple.config('PROP'),
                         reply_markup=inline.get_payment_info(payment_url))
    await state.clear()


async def change_prompt(call: types.CallbackQuery, state: FSMContext):
    prompt = await users.get_user_prompt(call.from_user.id)
    await call.message.edit_text(f"Old prompt: {prompt}\n\nSend me new prompt:")
    await state.set_state(ChangePrompt.new_prompt)


async def change_prompt_step_2(msg: types.Message, state: FSMContext):
    await users.new_prompt(msg.from_user.id, msg.text)
    await msg.answer("New prompt successfully saved! You can change it later in Profile section.",
                     reply_markup=inline.profile())
    await state.clear()


async def playground(call: types.CallbackQuery, state: FSMContext):
    if await users.get_user_prompt(tg_id=call.from_user.id):
        await call.message.edit_text(
            "Hello! This is playground for testing you prompt for email auto responses. "
            "Just send message here and wait for response.")
        await state.set_state(Playground.details)
    else:
        await call.message.edit_text(
            "In order to use the test, you need to add your description.", reply_markup=inline.new_prompt()
        )


async def playground_step_2(msg: types.CallbackQuery, state: FSMContext):
    user_prompt = await users.get_user_prompt(tg_id=msg.from_user.id)
    _, system_prompt = await texts.get_texts()
    response = await gpt.openai_engine.resp(msg.text, system_prompt, user_prompt)
    await msg.answer(f'<b>Answer for example:</b> {response}', reply_markup=inline.profile())
    await state.clear()


async def payment(call: types.CallbackQuery):
    payment_url, payment_id = stripe_engine.create_payment_link(call.from_user.id)
    status, _ = stripe_engine.check_payment_status(payment_id)
    await payments.create_new_payment(call.from_user.id, payment_id, status)
    if len(await users.all_users_subs()) > 14:
        await call.answer('Sorry, I only serve 10 users.')
    else:
        await call.message.edit_text("For use our service, you need pay service fee." + decouple.config('PROP'),
                                     reply_markup=inline.get_payment_info(payment_url))


async def register(dp: Dispatcher):
    dp.callback_query.register(handle_profile, F.data == 'profile')
    dp.callback_query.register(insert_new_prompt, F.data == 'new_prompt')
    dp.message.register(save_new_prompt, Prompt.new_prompt)
    dp.callback_query.register(change_prompt, F.data == 'change_prompt')
    dp.message.register(change_prompt_step_2, ChangePrompt.new_prompt)
    dp.callback_query.register(playground, F.data == 'playground')
    dp.message.register(playground_step_2, F.text, Playground.details, flags=({'long_operation': 'typing'}))
    dp.callback_query.register(payment, F.data == 'payment')
