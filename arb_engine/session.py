from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum


class SessionState(str, Enum):
    WAITING = "waiting"
    ACTIVE = "active"
    TARGET_REACHED = "target_reached"
    STOPPED = "stopped"


@dataclass
class ProfitSession:
    """A target-gated session.

    A session starts with an explicitly configured target. Once the target is
    reached it closes and will not open another session automatically.
    """

    target_profit_usd: float
    starter_capital_usd: float
    state: SessionState = SessionState.WAITING
    realized_profit_usd: float = 0.0
    started_at: datetime | None = None
    closed_at: datetime | None = None

    def start(self) -> None:
        if self.state not in (SessionState.WAITING, SessionState.TARGET_REACHED):
            raise RuntimeError(f"cannot start session from {self.state}")
        self.state = SessionState.ACTIVE
        self.realized_profit_usd = 0.0
        self.started_at = datetime.now(timezone.utc)
        self.closed_at = None

    def record_profit(self, amount_usd: float) -> bool:
        if self.state != SessionState.ACTIVE:
            return False
        if amount_usd < 0:
            # Losses are recorded but never treated as progress toward target.
            self.realized_profit_usd += amount_usd
            return False
        self.realized_profit_usd += amount_usd
        if self.realized_profit_usd >= self.target_profit_usd:
            self.state = SessionState.TARGET_REACHED
            self.closed_at = datetime.now(timezone.utc)
            return True
        return False

    @property
    def target_remaining_usd(self) -> float:
        return max(0.0, self.target_profit_usd - self.realized_profit_usd)

    def reset_for_manual_restart(self) -> None:
        self.state = SessionState.WAITING
        self.realized_profit_usd = 0.0
        self.started_at = None
        self.closed_at = None
