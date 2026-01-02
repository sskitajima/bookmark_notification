"""Mail content data structure."""

from dataclasses import dataclass


@dataclass
class MailContent:
    """Mail content data structure."""

    to: str
    from_addr: str
    subject: str
    content: str

    def __repr__(self) -> str:
        """String representation of MailContent."""
        return f"MailContent(to={self.to}, from_addr={self.from_addr}, subject={self.subject})"

