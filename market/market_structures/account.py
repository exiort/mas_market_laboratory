from __future__ import annotations
from typing import Dict, Tuple
from dataclasses import dataclass, field

from market.market_structures.accountview import AccountView



@dataclass
class Account:
    account_id:int
    agent_id:int

    cash:int
    shares:int

    reserved_cash:Dict[int, Tuple[int, int]] = field(default_factory=dict) #OrderID -> (quantity, price)
    reserved_shares:Dict[int, int] = field(default_factory=dict) #OrderID -> quantity

    deposited_cash:Dict[int, int] = field(default_factory=dict) #DepositID -> depositted + interest

    def create_view(self) -> AccountView:
        return AccountView(self)
