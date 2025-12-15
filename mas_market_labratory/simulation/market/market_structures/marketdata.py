from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple



@dataclass(frozen=True)
class MarketData:
    timestamp:float
    macro_tick:int
    micro_tick:int

    trade_count:int
    trade_volume:int
    
    last_traded_price:Optional[int]
    last_trade_size:Optional[int]
    
    L1_bids:Optional[Tuple[int, int, int]] #price - size - #of orders
    L1_asks:Optional[Tuple[int, int, int]] #price - size - #of orders

    
    spread:Optional[int]
    mid_price_x2:Optional[int]
    microprice_x_denom:Optional[Tuple[int, int]]
    
    L2_bids:Optional[Tuple[Tuple[int, int, int], ...]] # For each price level = price - size - #of orders
    L2_asks:Optional[Tuple[Tuple[int, int, int], ...]] # For each price level = price - size #of orders

    N:int
    bid_depth_N:int
    ask_depth_N:int
    imbalance_num_dem_N:Tuple[int, int]
    vwrap_num_dem:Tuple[int, int]
    
    
