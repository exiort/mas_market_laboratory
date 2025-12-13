from __future__ import annotations
from typing import Tuple
from dataclasses import dataclass



@dataclass(frozen=True)
class EconomyInsightView:
    macro_tick:int

    tv_interval:Tuple[float, float]
    deposit_rates:Tuple[Tuple[int, float], ...] #((term-rate), ...)
