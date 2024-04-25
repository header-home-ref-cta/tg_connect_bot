import aiohttp


async def check_credentials_api(email, password):
    api_url = 'http://127.0.0.1:5000/check_credentials'
    data = {'email': email, 'password': password}

    async with aiohttp.ClientSession() as session:
        response = await session.post(api_url, json=data)

    if response.status == 200:
        result = await response.json()
        return result['result']
    else:
        return False


async def run_task_api(email, password, user_prompt, system_prompt, tg_id):
    api_url = 'http://127.0.0.1:5000/run_task'
    data = {
        'email': email,
        'password': password,
        'user_prompt_text': user_prompt,
        'system_prompt_text': system_prompt,
        'tg_id': tg_id}

    async with aiohttp.ClientSession() as session:
        response = await session.post(api_url, json=data)

    if response.status == 200:
        result = await response.json()
        return result['result']
    else:
        return False
