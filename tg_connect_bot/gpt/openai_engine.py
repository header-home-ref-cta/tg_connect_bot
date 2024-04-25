import openai
from decouple import config


async def resp(prompt, system_prompt_text, user_prompt_text):
    system_prompt_text += f"Here is additional info about you as master: {user_prompt_text}" \
                          f"You need answer to message from new lead"
    openai.api_key = config("OPENAI_KEY")
    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[{'role': 'system', 'content': f'{system_prompt_text}'}, {"role": "user", "content": f"{prompt}"}],
            max_tokens=1200
        )
        model_response = response.choices[0]["message"]["content"]
        return model_response
    except openai.InvalidRequestError:
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[{'role': 'system', 'content': f'{system_prompt_text}'}, {"role": "user", "content": f"{prompt}"}],
            max_tokens=1200
        )
        model_response = response["choices"][0]["message"]["content"]
        return model_response