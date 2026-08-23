from __future__ import annotations

import json
import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class TelegramControl:
    """Small control-plane client.

    Telegram is notification/control only. The trading worker remains the
    authoritative process, so losing Telegram does not stop the engine.
    """

    def __init__(self, session, notifier):
        self.session = session
        self.notifier = notifier
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")

    def send(self, text: str) -> bool:
        if not self.token or not self.chat_id:
            return False
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        body = urlencode({"chat_id": self.chat_id, "text": text}).encode()
        try:
            with urlopen(Request(url, data=body, method="POST"), timeout=10) as r:
                return 200 <= r.status < 300
        except Exception:
            return False

    def status_text(self) -> str:
        return (
            f"Session: {self.session.state.value}\n"
            f"Target: ${self.session.target_profit_usd:.2f}\n"
            f"Profit: ${self.session.realized_profit_usd:.2f}\n"
            f"Remaining: ${self.session.target_remaining_usd:.2f}"
        )

    def handle_command(self, command: str) -> str:
        cmd = command.strip().lower()
        if cmd == "/status":
            return self.status_text()
        if cmd == "/start_session":
            self.session.start()
            return self.status_text()
        if cmd == "/stop_session":
            self.session.state = self.session.state.STOPPED
            return self.status_text()
        if cmd == "/new_session":
            self.session.reset_for_manual_restart()
            return "Session reset. Use /start_session to begin."
        return "Commands: /status /start_session /stop_session /new_session"
