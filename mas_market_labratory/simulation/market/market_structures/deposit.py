from __future__ import annotations
from dataclasses import dataclass

from simulation_configurations import get_simulation_configurations
from market_structures.depositview import DepositView



@dataclass(frozen=True)
class Deposit:
    deposit_id:int
    agent_id:int

    timestamp:float
    creation_macro_tick:int
    maturity_macro_tick:int
    
    deposited_cash:int
    interest_rate:float

    matured_cash:int


    def create_view(self) -> DepositView:
        SIM_CONFIG = get_simulation_configurations()
        
        return DepositView(
            deposit_id=self.deposit_id,
            agent_id=self.agent_id,
            creation_macro_tick=self.creation_macro_tick,
            maturity_macro_tick=self.maturity_macro_tick,
            deposited_cash=self.deposited_cash / SIM_CONFIG.PRICE_SCALE,
            interest_rate=self.interest_rate,
            matured_cash=self.matured_cash / SIM_CONFIG.PRICE_SCALE
        )
