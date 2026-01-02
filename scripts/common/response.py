"""Response data structure."""

from dataclasses import dataclass


@dataclass
class Response:
    """Response data structure."""

    code: int
    msg: str

    def __repr__(self) -> str:
        """String representation of Response."""
        return f"Response(code={self.code}, msg={self.msg})"

