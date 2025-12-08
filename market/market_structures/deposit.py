from __future__ import annotations
from dataclasses import dataclass



@dataclass(frozen=True)
class Deposit:
    deposit_id:int
    agent_id:int

    depositted_cash:float
    interest_rate:float
