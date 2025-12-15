from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple



@dataclass(frozen=True)
class MarketDataView:
    timestamp:float
    macro_tick:int
    micro_tick:int

    trade_count:int
    trade_volume:int

    last_traded_price:Optional[float]
    last_traded_size:Optional[float]

    L1_bids:Optional[Tuple[float, int, int]]
    L1_asks:Optional[Tuple[float, int, int]]

    spread:Optional[float]
    mid_price:Optional[float]
    microprice:Optional[float]

    L2_bids:Optional[Tuple[Tuple[float, int, int], ...]]
    L2_asks:Optional[Tuple[Tuple[float, int, int], ...]]

    N:int
    bid_depth_N:int
    ask_depth_N:int
    imbalance_N:Optional[float]
    vwrap:Optional[float]
    
