from __future__ import annotations

import os
import smtplib
import ssl
from email.message import EmailMessage
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class Notifier:
    def __init__(self):
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.smtp_host = os.getenv("SMTP_HOST")
        self.smtp_port = int(os.getenv("SMTP_PORT", "465"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.email_to = os.getenv("ALERT_EMAIL_TO")

    def telegram(self, text: str) -> bool:
        if not self.telegram_token or not self.telegram_chat_id:
            return False
        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        data = urlencode({"chat_id": self.telegram_chat_id, "text": text}).encode()
        try:
            req = Request(url, data=data, method="POST")
            with urlopen(req, timeout=10) as response:
                return 200 <= response.status < 300
        except Exception:
            return False

    def email(self, subject: str, body: str) -> bool:
        if not all([self.smtp_host, self.smtp_user, self.smtp_password, self.email_to]):
            return False
        msg = EmailMessage()
        msg["From"] = self.smtp_user
        msg["To"] = self.email_to
        msg["Subject"] = subject
        msg.set_content(body)
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, context=context) as smtp:
                smtp.login(self.smtp_user, self.smtp_password)
                smtp.send_message(msg)
            return True
        except Exception:
            return False

    def alert(self, subject: str, body: str) -> None:
        self.telegram(f"{subject}\n\n{body}")
        self.email(subject, body)
