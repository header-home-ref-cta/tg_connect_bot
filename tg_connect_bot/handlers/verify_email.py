import os, re, base64
import asyncio
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import aiohttp, decouple
from handlers import seledka, readMSG
from urllib.parse import quote_plus
from typing import Any, Dict


async def extract_link(message, link_type):
    # Regular expression pattern to match URLs
    url_pattern = r'https?://\S+'

    # Extract the email body
    for part in message['payload']['parts']:
        if part['mimeType'] == 'text/plain':
            data = part['body']['data']
            email_body = base64.urlsafe_b64decode(data).decode('utf-8')
            # Search for URLs in the email body using regular expressions
            urls = re.findall(url_pattern, email_body)
            # Find the URL containing the invitation link
            for url in urls:
                if link_type.lower() == "invitation":
                    if 'biz.yelp.com/signup/from_invite/' in url:
                        return url
                elif link_type.lower() == "confirm":
                    if 'biz.yelp.com/login/passwordless/' in url:
                        return url
            break


async def read_email(receiver: str, link_type: str):
    # Define criteria for searching emails
    query = f'subject:{link_type} from:yelp to:{quote_plus(receiver)}'

    # Authenticate and authorize access to Gmail API
    service, creds = await readMSG.authenticate()

    async with aiohttp.ClientSession() as session:
        # Search for emails matching the query
        while True:
            print("[read_email] Waiting for email...")
            await asyncio.sleep(1)
            response = await session.get(
                f"https://www.googleapis.com/gmail/v1/users/me/messages?q={query}",
                headers={"Authorization": f"Bearer {creds.token}"},
            )
            messages = await response.json()
            if messages.get('messages'):
                break
            if not messages.get('messages'):
                print('[read_email] No messages received.')

        # Get the latest email
        latest_email_id = messages['messages'][0]['id']
        response = await session.get(
            f"https://www.googleapis.com/gmail/v1/users/me/messages/{latest_email_id}",
            headers={"Authorization": f"Bearer {creds.token}"},
        )
        message = await response.json()

        # Extract the link from the email body
        target_link = (await extract_link(message, link_type))[:-1]

        # Open the invitation link in a web browser
        if target_link:
            print("[read_email] Required link returned")
            return target_link
        else:
            print("[read_email] No required link found in the email body.")


# example of use
async def verify_email(email,):

    try:
        driver = await seledka.browser_handler(headless=True)
        register_link = await asyncio.wait_for(read_email(email, "invitation"), timeout=244)
        print("[verify_email] REGLINK 1", register_link)
        if register_link: # account havenot registered
            await seledka.register_yelp(driver, register_link)
            print("[verify_email] VERIFY 2", register_link)
            register_link = await asyncio.wait_for(read_email(email, "confirm"), timeout=244)
            await seledka.confirm_yelp(driver, register_link)
            print("[verify_email] ASSIGN 3", register_link)
            await seledka.assing_alias(driver, email)
        return "[verify_email] Successfully registred yelp and assigned alias!]"
    except asyncio.TimeoutError:
        print("[verify_email] Task timed out after 4 minutes, aborting...")
    except Exception as e:
        print("[verify_email]", e)
    finally:
        driver.quit()

# asyncio.run(verify_email())
# asyncio.run(read_email("connecttoyelp+221@gmail.com", "invitation"))
