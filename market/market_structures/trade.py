from __future__ import annotations
from dataclasses import dataclass



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

    price:float
    quantity:int
    
    
