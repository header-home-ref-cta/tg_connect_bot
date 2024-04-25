from aiogram import types, Dispatcher, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from database import texts


class Admin(StatesGroup):
    text = State()


async def handle_admin(call: types.CallbackQuery, state: FSMContext):
    info_text, system_prompt_text = await texts.get_texts()
    TEXTS = {'info_text': info_text, 'system_prompt_text': system_prompt_text}
    for keys, value in TEXTS.items():
        if call.data in keys:
            await call.message.edit_text(f'<b>Current text:</b>\n{value}\n\n<b>Send new one:</b>')
            await state.set_state(Admin.text)
            await state.update_data(column=call.data.split("_text")[0])


async def handle_new_text(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    await texts.update_text(data['column'], msg.text)
    await state.clear()
    await msg.answer(f"Data successfully updated!\n\nNew text: {msg.text}")


async def register(dp: Dispatcher):
    dp.callback_query.register(handle_admin, F.data.endswith('_text'))
    dp.message.register(handle_new_text, Admin.text)
