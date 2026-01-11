"""Gmail sender implementation."""

import base64
from pathlib import Path
from typing import Optional
import logging

from email.message import EmailMessage
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from common.mail_content import MailContent
from common.response import Response

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.labels",
    "https://www.googleapis.com/auth/gmail.compose",
]


class MailSender:
    """Send emails using Gmail API."""

    def __init__(self, credential_path: str, token_path: Optional[str] = None):
        """Initialize MailSender.

        Args:
            credential_path: Path to Gmail API credentials JSON file
            token_path: Path to store/load OAuth token (default: same directory as credential_path)
        """
        self.credential_path = Path(credential_path)
        if token_path:
            self.token_path = Path(token_path)
        else:
            # Default to token.json in config directory
            self.token_path = self.credential_path.parent / "token.json"

    def _get_credential(self) -> Optional[Credentials]:
        """Get Gmail API credentials.

        Returns:
            Credentials object or None on failure
        """
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first time.
        if self.token_path.exists():
            logger.info(f"Loading credentials from {self.token_path}")
            try:
                creds = Credentials.from_authorized_user_file(
                    str(self.token_path), SCOPES
                )
            except Exception as e:
                logger.warning(f"Error loading credentials from token file: {e}")

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    logger.error(f"Error refreshing credentials: {e}")
                    creds = None
            else:
                if not self.credential_path.exists():
                    logger.error(f"Credential file not found: {self.credential_path}")
                    return None
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(self.credential_path), SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    logger.error(f"Error getting credentials: {e}")
                    return None

            # Save the credentials for the next run
            if creds:
                try:
                    with open(self.token_path, "w") as token:
                        token.write(creds.to_json())
                    logger.info(f"Credentials saved to {self.token_path}")
                except Exception as e:
                    logger.warning(f"Error saving credentials: {e}")

        return creds

    def send_email(self, mail_content: MailContent) -> Response:
        """Send an email message.

        Args:
            mail_content: MailContent object containing email details

        Returns:
            Response object indicating success or failure
        """
        creds = self._get_credential()
        if not creds:
            return Response(code=500, msg="Failed to get credentials")

        try:
            service = build("gmail", "v1", credentials=creds)
            message = EmailMessage()

            message.set_content(mail_content.content)
            message["To"] = mail_content.to
            message["From"] = mail_content.from_addr
            message["Subject"] = mail_content.subject

            # Encode message
            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            create_message = {"raw": encoded_message}
            send_message = (
                service.users()
                .messages()
                .send(userId="me", body=create_message)
                .execute()
            )

            logger.info(f"Email sent successfully. Message Id: {send_message['id']}")
            return Response(
                code=200,
                msg=f"Email sent successfully. Message Id: {send_message['id']}",
            )

        except HttpError as error:
            logger.error(f"An error occurred while sending email: {error}")
            return Response(code=500, msg=f"Failed to send email: {error}")
        except Exception as error:
            logger.error(f"Unexpected error while sending email: {error}")
            return Response(code=500, msg=f"Unexpected error: {error}")
