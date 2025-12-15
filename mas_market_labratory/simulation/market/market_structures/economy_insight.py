from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Tuple

from simulation_configurations import get_simulation_configurations
from market.market_structures.economy_insight_view import EconomyInsightView



@dataclass(frozen=True)
class EconomyInsight:
    macro_tick:int
    
    true_value:int
    short_rate:float

    width:float

    tv_interval:Tuple[int, int]
    deposit_rates:Dict[int, float] #((term-rate), ...)
    

    def create_view(self) -> EconomyInsightView:
        SIM_CONFIG = get_simulation_configurations()
        
        return EconomyInsightView(
            macro_tick=self.macro_tick,
            tv_interval=(self.tv_interval[0] / SIM_CONFIG.PRICE_SCALE, self.tv_interval[1] / SIM_CONFIG.PRICE_SCALE),
            deposit_rates=self.deposit_rates
        )
