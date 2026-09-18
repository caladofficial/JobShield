from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from app.core.config import settings


@dataclass
class EmailMessage:
    to: List[str]
    subject: str
    body_html: str
    body_text: str
    from_email: str
    from_name: Optional[str] = None
    attachments: Optional[List[Dict[str, Any]]] = None


@dataclass
class SendResult:
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None


class EmailProvider(ABC):
    @abstractmethod
    async def send(self, message: EmailMessage) -> SendResult:
        pass

    @abstractmethod
    async def send_test(self, to: str, subject: str, body: str) -> SendResult:
        pass

    @abstractmethod
    async def validate_connection(self) -> bool:
        pass

    @abstractmethod
    async def get_quota(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        pass


class GmailProvider(EmailProvider):
    def __init__(self, access_token: str, refresh_token: str):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.client_id = settings.GMAIL_CLIENT_ID
        self.client_secret = settings.GMAIL_CLIENT_SECRET

    async def send(self, message: EmailMessage) -> SendResult:
        return SendResult(success=False, error="Gmail API implementation pending")

    async def send_test(self, to: str, subject: str, body: str) -> SendResult:
        return SendResult(success=False, error="Gmail API implementation pending")

    async def validate_connection(self) -> bool:
        return bool(self.access_token)

    async def get_quota(self) -> Dict[str, Any]:
        return {"daily_limit": 500, "used": 0, "remaining": 500}

    async def disconnect(self) -> None:
        pass


class MicrosoftGraphProvider(EmailProvider):
    def __init__(self, access_token: str):
        self.access_token = access_token

    async def send(self, message: EmailMessage) -> SendResult:
        return SendResult(success=False, error="Microsoft Graph implementation pending")

    async def send_test(self, to: str, subject: str, body: str) -> SendResult:
        return SendResult(success=False, error="Microsoft Graph implementation pending")

    async def validate_connection(self) -> bool:
        return bool(self.access_token)

    async def get_quota(self) -> Dict[str, Any]:
        return {"daily_limit": 10000, "used": 0, "remaining": 10000}

    async def disconnect(self) -> None:
        pass


class SMTPProvider(EmailProvider):
    def __init__(self, host: str, port: int, username: str, password: str, from_email: str, use_tls: bool = True):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.from_email = from_email
        self.use_tls = use_tls

    async def send(self, message: EmailMessage) -> SendResult:
        return SendResult(success=False, error="SMTP implementation pending")

    async def send_test(self, to: str, subject: str, body: str) -> SendResult:
        return SendResult(success=False, error="SMTP implementation pending")

    async def validate_connection(self) -> bool:
        return bool(self.host and self.username and self.password)

    async def get_quota(self) -> Dict[str, Any]:
        return {"daily_limit": "unlimited", "used": 0, "remaining": "unlimited"}

    async def disconnect(self) -> None:
        pass


def get_email_provider(provider_type: str, credentials: Dict[str, str]) -> EmailProvider:
    if provider_type == "gmail":
        return GmailProvider(credentials.get("access_token", ""), credentials.get("refresh_token", ""))
    elif provider_type == "microsoft_graph":
        return MicrosoftGraphProvider(credentials.get("access_token", ""))
    elif provider_type == "smtp":
        return SMTPProvider(
            credentials.get("host", ""),
            int(credentials.get("port", 587)),
            credentials.get("username", ""),
            credentials.get("password", ""),
            credentials.get("from_email", ""),
        )
    else:
        raise ValueError(f"Unknown email provider: {provider_type}")