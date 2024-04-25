from database import functions


async def all_users():
    all_users_ids = await functions.select_function(
        columns=['*'],
        table='users',
        conditions=None,
        result='all'
    )
    all_users_ids_list = [user[0] for user in all_users_ids]
    return all_users_ids_list


async def all_users_subs():
    all_users_ids = await functions.select_function(
        columns=['*'],
        table='users',
        conditions=[f'subscription = TRUE'],
        result='all'
    )
    all_users_ids_list = [user[0] for user in all_users_ids]
    return all_users_ids_list


async def get_user_data(tg_id):
    gmail, app_password, subscription = await functions.select_function(
        columns=['email', 'app_password', 'subscription'],
        table='users',
        conditions=[f'tg_id = {tg_id}'],
        result='one'
    )
    return gmail, app_password, subscription


async def insert_new_user(tg_id, email, password):
    await functions.insert_function(
        table='users',
        insert_values={'tg_id': tg_id, 'email': email, 'app_password': password, 'subscription': False}
    )


async def get_user_prompt(tg_id):
    prompt = await functions.select_function(
        columns=['prompt'],
        table='users',
        conditions=[f'tg_id = {tg_id}'],
        result='one'
    )
    return prompt[0] if prompt else None


async def activate_subscription(tg_id):
    await functions.update_function(
        table='users',
        set_values={'subscription': True},
        conditions=[f'tg_id = {tg_id}']
    )


async def deactivate_subscription(tg_id):
    await functions.update_function(
        table='users',
        set_values={'subscription': False},
        conditions=[f'tg_id = {tg_id}']
    )
    await functions.delete_function(
        table='subscription',
        conditions=[f'tg_id = {tg_id}']
    )
    # await functions.update_function(
    #     table='payments',
    #     set_values={'status': 'open'},
    #     conditions=[f'tg_id = {tg_id}', 'status = complete']
    # )


async def check_subscription(tg_id):
    status = await functions.select_function(
        columns=['subscription'],
        table='users',
        conditions=[f'tg_id = {tg_id}'],
        result='one'
    )
    return status[0]


async def check_prompt(tg_id):
    prompt = await functions.select_function(
        columns=['prompt'],
        table='users',
        conditions=[f'tg_id = {tg_id}'],
        result='one'
    )
    return prompt[0] if prompt else None


async def new_prompt(tg_id, prompt):
    await functions.update_function(
        table='users',
        set_values={'prompt': prompt},
        conditions=[f'tg_id = {tg_id}']
    )


async def get_prompt_by_email(email):
    prompt = await functions.select_function(
        columns=['prompt'],
        table='users',
        conditions=[f'email = "{email}"'],
        result='one'
    )
    return prompt[0] if prompt else ''


async def run_task(tg_id):
    await functions.update_function(
        table='users',
        set_values={'run_task': True},
        conditions=[f'tg_id = {tg_id}']
    )


async def disable_task(tg_id):
    await functions.update_function(
        table='users',
        set_values={'run_task': False},
        conditions=[f'tg_id = {tg_id}']
    )


async def task_status(tg_id):
    status = await functions.select_function(
        columns=['run_task'],
        table='users',
        conditions=[f'tg_id = {tg_id}'],
        result='one'
    )
    return status

async def insert_new_email(tg_id, email):
    await functions.insert_function(
        table='used_emails',
        insert_values={'tg_id': tg_id, 'email': email}
    )

async def get_email_count():
    all_emails_ids = await functions.select_function(
        columns=['*'],
        table='used_emails',
        conditions=None,
        result='all'
    )
    # all_users_ids_list = [user[0] for user in all_users_ids]
    return len(all_emails_ids)

async def get_email(tg_id):
    email = await functions.select_function_pay(
        columns=['email'],
        table='used_emails',
        conditions=[f'tg_id = {tg_id}'],
        result='one'
    )
    return email[0] if email else ''

async def get_tg_id_by_email(email):
    tg_id = await functions.select_function_email(
        columns=['tg_id'],
        table='users',
        email=email,
        result='one'
    )
    return tg_id[0] if tg_id else ''


async def get_task_status_by_email(email):
    task_status = await functions.select_function_email(
        columns=['run_task'],
        table='users',
        email=email,
        result='one'
    )
    return task_status[0] if task_status else ''

