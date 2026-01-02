"""Mail content writer."""

from typing import Optional

from common.bookmark import Bookmark
from common.logger import setup_logger
from common.mail_content import MailContent

logger = setup_logger(__name__)


class MailWriter:
    """Write email content from bookmarks."""

    def write_email(
        self,
        bookmarks: list[Bookmark],
        to_addr: str,
        from_addr: str,
        subject: Optional[str] = None,
    ) -> MailContent:
        """Write email content from list of bookmarks.

        Args:
            bookmarks: List of Bookmark objects to include in email
            to_addr: Recipient email address
            from_addr: Sender email address
            subject: Email subject (default: auto-generated)

        Returns:
            MailContent object
        """
        if not bookmarks:
            logger.warning("No bookmarks provided, creating empty email")
            content = "No bookmarks to display."
        else:
            content_lines = [f"Found {len(bookmarks)} bookmark(s):\n"]
            for i, bookmark in enumerate(bookmarks, 1):
                content_lines.append(f"{i}. {bookmark.title}")
                content_lines.append(f"   URL: {bookmark.url}")
                if bookmark.tags:
                    content_lines.append(f"   Tags: {', '.join(bookmark.tags)}")
                content_lines.append("")

            content = "\n".join(content_lines)

        if subject is None:
            if bookmarks:
                subject = f"[Bot] Bookmark Notification - {len(bookmarks)} item(s)"
            else:
                subject = "[Bot] Bookmark Notification"

        logger.info(f"Created email content with {len(bookmarks)} bookmark(s)")

        return MailContent(
            to=to_addr,
            from_addr=from_addr,
            subject=subject,
            content=content,
        )
