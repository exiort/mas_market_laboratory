from __future__ import annotations
from typing import Dict, Tuple
from dataclasses import dataclass, field



@dataclass
class Account:
    account_id:int
    agent_id:int

    cash:float
    shares:int

    reserved_cash:Dict[int, Tuple[int, float]] = field(default_factory=dict) #OrderID -> (quantity, price)
    reserved_shares:Dict[int, int] = field(default_factory=dict) #OrderID -> quantity

    deposited_cash:Dict[int, float] = field(default_factory=dict) #DepositID -> depositted + interest
