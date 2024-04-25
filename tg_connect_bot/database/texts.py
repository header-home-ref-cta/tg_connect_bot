from database import functions


async def get_texts():
    info_text, system_prompt_text = await functions.select_function(
        columns=['info', 'system_prompt'],
        table='texts',
        conditions=None,
        result='one'
    )
    return info_text, system_prompt_text


async def update_text(column, text):
    await functions.update_function(
        table='texts',
        set_values={column: text},
        conditions=None
    )
