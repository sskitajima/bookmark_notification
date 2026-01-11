"""Content manager for selecting bookmarks to publish."""

import random
from typing import Optional
import logging

from common.bookmark import Bookmark

logger = logging.getLogger(__name__)


class ContentManager:
    """Manage content selection from bookmarks."""

    def select_publish_content(
        self, bookmarks: list[Bookmark], count: Optional[int] = None
    ) -> list[Bookmark]:
        """Select bookmarks to publish.

        Args:
            bookmarks: List of all bookmarks
            count: Number of bookmarks to select (default: 1, or all if less than count)

        Returns:
            List of selected Bookmark objects
        """
        if not bookmarks:
            logger.warning("No bookmarks provided")
            return []

        if count is None:
            count = 1

        # If we have fewer bookmarks than requested, return all
        if len(bookmarks) <= count:
            logger.info(f"Selecting all {len(bookmarks)} bookmark(s)")
            return bookmarks

        # Randomly select bookmarks
        selected = random.sample(bookmarks, count)
        logger.info(f"Selected {len(selected)} bookmark(s) from {len(bookmarks)} total")

        return selected

