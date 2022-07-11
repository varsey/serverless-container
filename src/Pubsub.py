import os
import logging
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


class Pubsub:
    @staticmethod
    def run_pubsub_watch(log: logging):
        """
        subscribe gmail api to pubsub for pushing notification massages
        Downlaod credentials.json from google cloud first
        run for the first time and get a link for authorization -> click it and token.json appears
        """
        creds = None
        tokenfilename = os.getcwd() + '/creds/token.json'
        if os.path.exists(tokenfilename):
            creds = Credentials.from_authorized_user_file(tokenfilename, SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(os.getcwd() + '/creds/credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open(tokenfilename, 'w') as token:
                token.write(creds.to_json())

        try:
            service = build('gmail', 'v1', credentials=creds)
            request = {
                'labelIds': ['INBOX'],
                'topicName': os.getenv('PUBSUB_TOPIC')
            }
            log.info(
                service.users().watch(userId='me', body=request).execute()
            )
            log.info('watching topic initiated')
        except HttpError as error:
            log.error(f'An error occurred: {error}')

        return None
