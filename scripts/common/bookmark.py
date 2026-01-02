"""Bookmark data structure."""

from dataclasses import dataclass


@dataclass
class Bookmark:
    """Bookmark data structure."""

    id: int
    title: str
    url: str
    tags: list[str]

    def __repr__(self) -> str:
        """String representation of Bookmark."""
        return f"Bookmark(id={self.id}, title={self.title}, url={self.url}, tags={self.tags})"

