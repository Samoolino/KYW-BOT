from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Allocation:
    name: str
    percent: float
    destination: str


class ProfitAllocator:
    """Calculates allocations without moving funds.

    Destinations are labels/account identifiers only. This module deliberately
    does not perform withdrawals or transfer private keys.
    """

    def __init__(self, allocations: list[Allocation]):
        total = sum(a.percent for a in allocations)
        if abs(total - 100.0) > 1e-6:
            raise ValueError("allocation percentages must total 100")
        if any(a.percent < 0 for a in allocations):
            raise ValueError("allocation percentage cannot be negative")
        self.allocations = allocations

    def allocate_profit(self, profit_usd: float) -> dict[str, float]:
        if profit_usd < 0:
            raise ValueError("profit must be non-negative")
        return {a.name: profit_usd * a.percent / 100 for a in self.allocations}

    def allocate_starter(self, starter_usd: float) -> dict[str, float]:
        if starter_usd < 0:
            raise ValueError("starter capital must be non-negative")
        return {a.name: starter_usd * a.percent / 100 for a in self.allocations}
