from __future__ import annotations
from typing import Optional, Dict
from enum import Enum
from dataclasses import dataclass, field

from market.market_structures.trade import Trade



class OrderType(Enum):
    LIMIT = 1
    MARKET = 2


class Side(Enum):
    BUY = 1
    SELL = 2


class OrderStatus(Enum):
    PENDING = 1          
    OPEN = 2             
    PARTIALLY_FILLED = 3 
    FILLED = 4           
    CANCELED = 5         
    EXPIRED = 6          
    REJECTED = 7         


@dataclass
class Order:
    order_id:int
    agent_id:int

    timestamp:float
    macro_tick:int
    micro_tick:int

    order_type:OrderType
    side:Side

    quantity:int
    price:Optional[float]

    status:OrderStatus
    remaining_quantity:int = field(init=False)
    
    avarage_trade_price:float
    trades:Dict[int, Trade] = field(default_factory=dict)
    

    def __post_init__(self) -> None:
        self.remaining_quantity = self.quantity

    
