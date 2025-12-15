from __future__ import annotations
from typing import Dict, Tuple

from simulation_configurations import get_simulation_configurations
from market.market_structures.account import Account



class AccountView:
    def __init__(self, account:Account) -> None:
        self.__account = account

        
    def account_id(self) -> int:
        return self.__account.account_id


    def agent_id(self) -> int:
        return self.__account.agent_id


    def cash(self) -> float:
        SIM_CONFIG = get_simulation_configurations()
        return self.__account.cash / SIM_CONFIG.PRICE_SCALE


    def shares(self) -> int:
        return self.__account.shares


    def reserved_cash(self) -> Dict[int, Tuple[int, int]]:
        return self.__account.reserved_cash.copy()


    def reserved_shares(self) -> Dict[int, int]:
        return self.__account.reserved_shares.copy()


    def deposited_cash(self) -> Dict[int, int]:
        return self.__account.deposited_cash.copy()
