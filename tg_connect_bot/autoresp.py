import contextlib
import asyncio
from urllib.parse import quote_plus, unquote_plus
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from handlers import seledka
from gpt import openai_engine
from database import users, texts, creation
from handlers.readMSG import authenticate, get_receiver, mark_as_read
from configuration.notify_client import tcp_echo_client
import logging, decouple
import json


logging.basicConfig(
    level=logging.DEBUG,
    format=u'[%(asctime)s] - %(message)s',
    handlers=[
        logging.FileHandler(decouple.config("PATH_TO_LOGS"), mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ] if decouple.config("PATH_TO_LOGS") else [logging.StreamHandler()]
)


async def log_in():
    driver = None
    driver = await seledka.browser_handler(headless=True)
    driver.set_window_size(1024, 768)
    while True:
        try:
            driver.get('https://mail.google.com/mail/u/0/')
            WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            if driver.current_url.startswith('https://accounts.google.com'):
                login = decouple.config('OUR_EMAIL')
                your_password = decouple.config('OUR_EMAIL_PASS')
                driver.implicitly_wait(15)
                email_field = driver.find_element(By.ID, 'identifierId').send_keys(login)
                next_button = driver.find_element(By.ID, 'identifierNext').click()
                wait = WebDriverWait(driver, 10)
                password_field = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="password"]')))
                password_field.send_keys(your_password)
                driver.find_element(By.ID, 'passwordNext').click()
                await asyncio.sleep(10)
                print("[autoresp] LOGGED IN")
            if not driver.current_url.startswith("https://mail.google.com/mail/"):
                print(f"[autoresp] {driver.current_url}")
                continue
            break
        except Exception as e:
            logging.exception(f'[autoresp] LOGGING ERROR:\n{e}')
            continue
    return driver


async def read(driver, receiver, subject):
    letter = None
    url = driver.current_url
    url = url[:33] +"/#search/"+ quote_plus(
        f'is:unread to:({receiver})')
    # f'is:unread subject:(you received new) from:("yelp inbox")')
    driver.get(url)
    logging.debug("[autoresp] GET " + url)
    # wait = WebDriverWait(driver, 10)
    # wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="main"]')))
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    await asyncio.sleep(0)
    try:
        email_subject = driver.find_element(By.CSS_SELECTOR,
                                            'table[role="grid"] tr[role="row"] td[role="gridcell"]')
        email_subject.click()
        await asyncio.sleep(0)
        wait = WebDriverWait(driver, 10)
        if ("a new lead on Yelp" in subject):
            letter = wait.until(EC.presence_of_element_located((By.XPATH, "//div[3]/div/div[2]/div/div[4]"))) 
            letter = letter.text
            # receiver = driver.find_element(By.XPATH, "//td/table/tbody/tr/td/div/span/span").text
            # driver.find_element(By.CSS_SELECTOR, 'div[data-tooltip="Show details"]').click()
            # receiver = driver.find_element(By.XPATH, '//tr[2]/td[2]/span/span').text
            # receiver = receiver.split("<")[-1][:-1]
        elif ("requesting a quote from" in subject):
            letter = wait.until(EC.presence_of_element_located((By.XPATH, "//table[9]/tbody/tr/td/div/p")))
            letter = letter.text
    except Exception as e:
        logging.debug("[autoresp] Email not found")
        logging.exception(f"[autoresp] {e}")
    finally:
        return driver, letter


async def read_msgs(service):
    results = service.users().messages().list(userId='me',
                                              labelIds=['UNREAD']).execute()  # get unread messages from server
    messages = results.get('messages', [])  # get unread messages from server
    return messages


async def form_response(receiver, letter, ):
    response = None
    try:
        await asyncio.sleep(0)
        # magic_number = receiver.split("@")[0].split("+")[-1]
        tg_id = await users.get_tg_id_by_email(receiver)
        user_prompt = await users.get_user_prompt(tg_id=tg_id)
        _, system_prompt = await texts.get_texts()
        response = await openai_engine.resp(letter, system_prompt, user_prompt)
    except Exception as e:
        logging.exception(f"[autoresp] FORM RESPONSE ERROR {e}")
    finally:
        return response


async def send_response(driver, response):
    driver.implicitly_wait(15)
    reply_btn = driver.find_element(By.CSS_SELECTOR, 'div[data-tooltip="Reply"]').click()
    reply_btn = driver.find_element(By.CSS_SELECTOR, 'div[role="textbox"]').send_keys(response)
    await asyncio.sleep(0)
    # reply_btn = driver.find_element(By.CSS_SELECTOR, 'div[data-tooltip="Send (Ctrl-Enter)"]')
    # driver.find_element(By.XPATH, "//div[3]/div/div/div/div/div/div/div[2]/div/table/tbody/tr/td[4]/div[2]").click()
    # driver.find_element(By.XPATH, "//div[3]/div/table/tbody/tr/td[2]/div[2]/div").send_keys(response)
    driver.find_element(By.XPATH, "//div[4]/table/tbody/tr/td/div/div[2]/div").click()
    logging.debug(f'[autoresp] EMAIL SENT')
    # wait = WebDriverWait(driver, 10)
    # ref = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[2]/div/div[2]/div[2]/div[2]/div/div")))
    # ref.click()
    # driver.find_element(By.XPATH, '//div[2]/div/div/div/div/div/div/div[2]/div[2]/div/div').click()
    return driver


async def main():
    driver = await log_in()
    if not driver:
        logging.exception("[autoresp] LOGIN FAILED, PROBLEM IN [seledka]!!!")
        return
    service, _ = await authenticate()
    # tg_id = receiver.split("@")[0].split("+")[-1]
    while True:
        try:
            await asyncio.sleep(7)
            messages = await read_msgs(service)
            if not messages:
                logging.debug(f"[autoresp] NO EMAILS DETECTED")
                continue
            for message in messages:
                logging.debug('---------------------------------------------------------')
                msg = service.users().messages().get(userId='me',
                                                     id=message['id']).execute()  # get each message from server
                subject = msg['payload']['headers'][17]['value']
                #  or not "requesting a quote from" in subject
                if ("a new lead on Yelp" not in subject) and ("requesting a quote from" not in subject):
                    logging.debug(f'[autoresp] Marked as read: {subject}')
                    await mark_as_read(service, message['id'])
                    continue
                receiver = await get_receiver(msg)
                if not receiver or not await users.get_task_status_by_email(receiver):
                    logging.debug(f'[autoresp]: {receiver} NOT RUN TASK')
                    await mark_as_read(service, message['id'])
                    continue
                logging.debug(f'[autoresp]      to: {receiver}')
                # logging.debug('[autoresp] Snippet:', msg['snippet'])
                driver, letter = await read(driver, receiver, subject)
                if not letter:
                    logging.debug(f'[autoresp] NO LETTER FOUND')
                    continue
                logging.debug(f'[autoresp] LETTER FOUND:\n{letter}')
                response = await form_response(receiver, letter)
                logging.debug(f'[autoresp] RESPONSE:\n{response}')
                if not response:
                    logging.debug('[autoresp] NO RESPONCE')
                    continue
                    # await mark_as_read(service, message['id'])
                driver = await send_response(driver, response)
                await tcp_echo_client(receiver, letter, response)

        except ConnectionRefusedError as e:
            logging.exception(f"[tcp_echo_client] ConnectionRefusedError {e}")
        except Exception as e:
            logging.exception(f'[autoresp] ERROR IN MAIN\n{e}')
       


# Run the main coroutine
# receiver = 'connecttoyelp+9@gmail.com'
# tg_id = receiver.split("@")[0].split("+")[-1]
# asyncio.run(login_read(receiver))
# driver = asyncio.run(log_in())
with contextlib.suppress(KeyboardInterrupt, SystemExit):
    asyncio.run(main())
