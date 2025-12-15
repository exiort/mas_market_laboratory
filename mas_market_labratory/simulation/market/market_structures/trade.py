from __future__ import annotations
from dataclasses import dataclass

from simulation_configurations import get_simulation_configurations
from market.market_structures.tradeview import TradeView



@dataclass(frozen=True)
class Trade:
    trade_id:int
    
    timestamp:float
    macro_tick:int
    micro_tick:int

    seller_agent_id:int
    sell_order_id:int

    buyer_agent_id:int
    buy_order_id:int

    price:int
    quantity:int
    
    
    def create_view(self) -> TradeView:
        SIM_CONFIG = get_simulation_configurations()
        
        return TradeView(
            trade_id=self.trade_id,
            timestamp=self.timestamp,
            macro_tick=self.macro_tick,
            micro_tick=self.micro_tick,
            price=self.price / SIM_CONFIG.PRICE_SCALE,
            quantity=self.quantity
        )
