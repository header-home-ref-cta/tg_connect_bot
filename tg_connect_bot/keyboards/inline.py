from aiogram.utils.keyboard import InlineKeyboardBuilder


def admin():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Change info text", callback_data='info_text')
    keyboard.button(text="Change system prompt text", callback_data='system_prompt_text')
    return keyboard.as_markup()


def get_start():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="📡 Connect service", callback_data='connect_service')
    keyboard.button(text="👤 My Profile", callback_data='profile')
    return keyboard.as_markup()


def profile():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="👤 My Profile", callback_data='profile')
    return keyboard.as_markup()


def new_user():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="📡 Connect service", callback_data='connect_service')
    return keyboard.as_markup()

def email_done():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Done", callback_data='connect_email_step2')
    return keyboard.as_markup()

def connect_service():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Use our email", callback_data='our_email')
    keyboard.button(text="I wanna connect my email", callback_data='my_email')
    return keyboard.as_markup()


def get_payment_url(url):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Payment", url=url)
    return keyboard.as_markup()


def get_payment_info(url):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Payment", url=url)
    keyboard.button(text="Check payment", callback_data="check_payment")
    return keyboard.as_markup()


def main_menu():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Main Menu", callback_data='main_menu')
    return keyboard.as_markup()


def new_prompt():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Create new prompt", callback_data='new_prompt')
    return keyboard.as_markup()


def in_profile(sub, task_status, conf_sub_url):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Playground", callback_data='playground')
    keyboard.button(text="Change prompt", callback_data='change_prompt')
    if sub == "Not subscribed":
        keyboard.button(text="Payment", callback_data="payment")
    else:
        if task_status[0] == 0:
            keyboard.button(text='Run task', callback_data='run_task')
        else:
            keyboard.button(text='Stop task', callback_data='stop_task')
        keyboard.button(text="Configure subscription", url=conf_sub_url)
    return keyboard.as_markup()

