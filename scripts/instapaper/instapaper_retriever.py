"""Instapaper bookmark retriever."""

from typing import Optional

import requests
from requests_oauthlib import OAuth1

from common.bookmark import Bookmark
from common.logger import setup_logger

logger = setup_logger(__name__)


class InstapaperRetriever:
    """Retrieve bookmarks from Instapaper."""

    BASE_URL = "https://www.instapaper.com/api/1"
    BOOKMARKS_LIST_URL = f"{BASE_URL}/bookmarks/list"
    ACCESS_TOKEN_URL = f"{BASE_URL}/oauth/access_token"

    def __init__(
        self,
        consumer_key: str,
        consumer_secret: str,
        x_auth_username: str,
        x_auth_password: str,
    ):
        """Initialize InstapaperRetriever.

        Args:
            consumer_key: Instapaper consumer key
            consumer_secret: Instapaper consumer secret
            x_auth_username: Instapaper username
            x_auth_password: Instapaper password
        """
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.x_auth_username = x_auth_username
        self.x_auth_password = x_auth_password
        self._oauth_token: Optional[str] = None
        self._oauth_token_secret: Optional[str] = None

    def _get_access_token(self) -> tuple[Optional[str], Optional[str]]:
        """Get OAuth access token from Instapaper.

        Returns:
            Tuple of (oauth_token, oauth_token_secret) or (None, None) on failure
        """
        auth = OAuth1(self.consumer_key, self.consumer_secret)
        params = {
            "x_auth_username": self.x_auth_username,
            "x_auth_password": self.x_auth_password,
            "x_auth_mode": "client_auth",
        }

        try:
            response = requests.post(
                self.ACCESS_TOKEN_URL, auth=auth, data=params, timeout=30
            )

            if response.status_code != 200:
                logger.error(
                    f"Failed to get access token: {response.status_code}, {response.text}"
                )
                return None, None

            # Extract tokens from response
            token_data = dict(item.split("=") for item in response.text.split("&"))
            oauth_token = token_data.get("oauth_token")
            oauth_token_secret = token_data.get("oauth_token_secret")

            return oauth_token, oauth_token_secret
        except Exception as e:
            logger.error(f"Error getting access token: {e}")
            return None, None

    def _get_bookmarks_from_server(
        self, limit: int = 500, folder_id: str = "unread"
    ) -> list[dict]:
        """Get bookmarks from Instapaper server.

        Args:
            limit: Maximum number of bookmarks to retrieve
            folder_id: Folder ID to retrieve from (default: "unread")

        Returns:
            List of bookmark dictionaries
        """
        if not self._oauth_token or not self._oauth_token_secret:
            self._oauth_token, self._oauth_token_secret = self._get_access_token()
            if not self._oauth_token or not self._oauth_token_secret:
                logger.error("Failed to get access token")
                return []

        auth = OAuth1(
            self.consumer_key,
            self.consumer_secret,
            self._oauth_token,
            self._oauth_token_secret,
        )
        payload = {"limit": limit, "folder_id": folder_id}

        try:
            response = requests.post(
                self.BOOKMARKS_LIST_URL, auth=auth, data=payload, timeout=30
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get bookmarks: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error getting bookmarks from server: {e}")
            return []

    def _generate_bookmark_object(self, item: dict) -> Optional[Bookmark]:
        """Generate Bookmark object from API response item.

        Args:
            item: Bookmark item from API response

        Returns:
            Bookmark object or None if invalid
        """
        if item.get("type", "") != "bookmark":
            return None

        bookmark_id = item.get("bookmark_id")
        if bookmark_id is None:
            return None

        try:
            return Bookmark(
                id=int(bookmark_id),
                title=item.get("title", ""),
                url=item.get("url", ""),
                tags=[tag.get("name", "") for tag in item.get("tags", [])],
            )
        except (ValueError, TypeError) as e:
            logger.warning(f"Error generating bookmark object: {e}")
            return None

    def retrieve_bookmark(
        self, limit: int = 500, folder_id: str = "unread"
    ) -> list[Bookmark]:
        """Retrieve bookmarks from Instapaper.

        Args:
            limit: Maximum number of bookmarks to retrieve
            folder_id: Folder ID to retrieve from (default: "unread")

        Returns:
            List of Bookmark objects
        """
        logger.info(f"Retrieving bookmarks (limit={limit}, folder_id={folder_id})")
        res_json = self._get_bookmarks_from_server(limit=limit, folder_id=folder_id)

        bookmarks = []
        for item in res_json:
            bookmark = self._generate_bookmark_object(item)
            if bookmark:
                bookmarks.append(bookmark)

        logger.info(f"Retrieved {len(bookmarks)} bookmarks")
        return bookmarks
