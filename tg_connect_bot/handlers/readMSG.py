from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64, os, asyncio, decouple
import quopri  # for decoding quoted-printable content

# Define the scopes required for accessing Gmail API


async def authenticate():
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://mail.google.com']
    # Load or create credentials
    token_path = decouple.config('GMAIL_TOKEN_PATH')
    creds_path = decouple.config('GMAIL_CREDENTIALS_PATH')
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    print('[readMSG] Authentication successful')
    return service, creds


async def get_receiver(msg):
    return msg['payload']['headers'][0]['value']

async def mark_as_read(service, message_id):
    service.users().messages().modify(
        userId='me',
        id=message_id,
        body={'removeLabelIds': ['UNREAD']}
    ).execute()

async def mark_as_UNread(service, message_id):
    service.users().messages().modify(
        userId='me',
        id=message_id,
        body={'removeLabelIds': ['UNREAD']}
    ).execute()


async def main(service):
    while True:
        await asyncio.sleep(5)
        results = service.users().messages().list(userId='me', labelIds=['UNREAD']).execute() # get unread messages from server
        messages = results.get('messages', []) # get unread messages from server
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute() # get each message from server
            subject = msg['payload']['headers'][17]['value']
            if "a new lead on Yelp" in subject:
                print('[readMSG]      to:', msg['payload']['headers'][0]['value'])
                print('[readMSG] Snippet:', msg['snippet'])
                print('---------------------------------------------------------')



    # THE BEST CODE EVER
    # if not messages:
    #     print("No messages found.")
    # else:
    #     print("Messages:")
    #     a = 0
    #     for message in messages:
    #         print(a);a+=1
    #         msg = service.users().messages().get(userId='me', id=message['id']).execute()
    #         if 'UNREAD' in msg['labelIds']:
    #             print(f"From: {msg['payload']['headers'][3]['value']}")
    #             print(f"Subject: {msg['payload']['headers'][17]['value']}")
    #             print(f"Date: {msg['payload']['headers'][1]['value']}")
    #             print(f"Snippet: {msg['snippet']}")
    #             print("--------------------------------------------------")
    #


if __name__ == '__main__':
    service, creds = asyncio.run(authenticate())
    asyncio.run(main(service))
