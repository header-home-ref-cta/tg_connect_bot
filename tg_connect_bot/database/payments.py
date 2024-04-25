from database import functions


async def create_new_payment(tg_id, payment_id, status):
    await functions.insert_function(
        table='payments',
        insert_values={'tg_id': tg_id, 'payment_id': payment_id, 'status': status}
    )


async def update_payment_status(tg_id, status):
    await functions.update_function_pay(
        table='payments',
        set_values={'status': status},
        conditions=[f'tg_id = {tg_id}']
    )


async def get_transaction(tg_id):
    payment_id = await functions.select_function_pay(
        columns=['payment_id'],
        table='payments',
        conditions=[f"tg_id = {tg_id}"],
        result="one"
    )
    return payment_id


async def add_subscription(tg_id, date_start, date_end):
    await functions.insert_function(
        table='subscription',
        insert_values={'tg_id': tg_id, 'subscription_start': date_start, 'subscription_end': date_end}
    )


async def get_subscription_end_date(tg_id):
    date_end = await functions.select_function(
        columns=['subscription_end'],
        table='subscription',
        conditions=[f"tg_id = {tg_id}"],
        result="one"
    )
    return date_end
