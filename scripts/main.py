"""Main entry point for bookmark notification application."""

import sys
from pathlib import Path

# Add scripts directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent))

import yaml

from common.content_manager import ContentManager
from common.logger import setup_logger
from instapaper.instapaper_retriever import InstapaperRetriever
from mail.mail_sender import MailSender
from mail.mail_writer import MailWriter

logger = setup_logger(__name__)


def load_config(config_path: Path) -> dict:
    """Load configuration from YAML file.

    Args:
        config_path: Path to config YAML file

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If config file is invalid
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    if config is None:
        config = {}

    return config


def main():
    """Main application entry point."""
    try:
        # Load configuration
        config_path = Path(__file__).parent.parent / "config" / "config.yaml"
        config = load_config(config_path)
        logger.info(f"Loaded configuration from {config_path}")

        # Get Instapaper configuration
        instapaper_config = config.get("instapaper", {})
        consumer_key = instapaper_config.get("consumer_key")
        consumer_secret = instapaper_config.get("consumer_secret")
        username = instapaper_config.get("username")
        password = instapaper_config.get("password")

        if not all([consumer_key, consumer_secret, username, password]):
            logger.error("Missing Instapaper configuration")
            return 1

        # Get mail configuration
        mail_config = config.get("mail", {})
        to_addr = mail_config.get("to")
        from_addr = mail_config.get("from")
        credential_path = mail_config.get("credential_path")

        if not all([to_addr, from_addr, credential_path]):
            logger.error("Missing mail configuration")
            return 1

        # Get application configuration
        app_config = config.get("app", {})
        bookmark_limit = app_config.get("bookmark_limit", 500)
        bookmark_count = app_config.get("bookmark_count", 1)
        folder_id = app_config.get("folder_id", "unread")

        # Initialize components
        retriever = InstapaperRetriever(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            x_auth_username=username,
            x_auth_password=password,
        )

        content_manager = ContentManager()
        mail_writer = MailWriter()
        mail_sender = MailSender(credential_path=credential_path)

        # Retrieve bookmarks
        logger.info("Retrieving bookmarks from Instapaper")
        bookmarks = retriever.retrieve_bookmark(
            limit=bookmark_limit, folder_id=folder_id
        )

        if not bookmarks:
            logger.warning("No bookmarks retrieved")
            return 0

        # Select bookmarks to publish
        logger.info("Selecting bookmarks to publish")
        selected_bookmarks = content_manager.select_publish_content(
            bookmarks, count=bookmark_count
        )

        if not selected_bookmarks:
            logger.warning("No bookmarks selected")
            return 0

        # Write email content
        logger.info("Writing email content")
        mail_content = mail_writer.write_email(
            bookmarks=selected_bookmarks,
            to_addr=to_addr,
            from_addr=from_addr,
        )

        # Send email
        logger.info("Sending email")
        response = mail_sender.send_email(mail_content)

        if response.code == 200:
            logger.info("Email sent successfully")
            return 0
        else:
            logger.error(f"Failed to send email: {response.msg}")
            return 1

    except FileNotFoundError as e:
        logger.error(f"Configuration file not found: {e}")
        return 1
    except yaml.YAMLError as e:
        logger.error(f"Error parsing configuration file: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
