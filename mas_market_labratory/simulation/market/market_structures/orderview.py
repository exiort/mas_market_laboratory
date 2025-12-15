from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple

from simulation_configurations import get_simulation_configurations
from market.market_structures.order import Order, OrderType, Side, OrderLifecycle, OrderEndReasons
from market.market_structures.tradeview import TradeView



@dataclass
class OrderView:
    def __init__(self, order:Order) -> None:
        self.__order = order

        
    @property
    def order_id(self) -> int:
        return self.__order.order_id

    
    @property
    def agent_id(self) -> int:
        return self.__order.agent_id

    
    @property
    def timestamp(self) -> float:
        return self.__order.timestamp


    @property
    def macro_tick(self) -> int:
        return self.__order.macro_tick

    
    @property
    def micro_tick(self) -> int:
        return self.__order.micro_tick


    @property
    def order_type(self) -> OrderType:
        return self.__order.order_type


    @property
    def side(self) -> Side:
        return self.__order.side


    @property
    def quantity(self) -> int:
        return self.__order.quantity


    @property
    def price(self) -> Optional[float]:
        if self.__order.price is None:
            return None

        SIM_CONFIG = get_simulation_configurations()
        return self.__order.price / SIM_CONFIG.PRICE_SCALE
    

    @property
    def lifecycle(self) -> OrderLifecycle:
        return self.__order.lifecycle


    @property
    def end_reason(self) -> OrderEndReasons:
        return self.__order.end_reason


    @property
    def remaining_quantity(self) -> int:
        return self.__order.remaining_quantity


    @property
    def average_trade_price(self) -> Optional[float]:
        if self.__order.average_trade_price is None:
            return None

        SIM_CONFIG = get_simulation_configurations()
        return self.__order.average_trade_price / SIM_CONFIG.PRICE_SCALE

    
    @property
    def trades(self) -> Tuple[TradeView]:
        SIM_CONFIG = get_simulation_configurations()

        trade_views = []
        for trade in self.__order.trades.values():
            trade_views.append(TradeView(
                trade_id=trade.trade_id,
                timestamp=trade.timestamp,
                macro_tick=trade.macro_tick,
                micro_tick=trade.micro_tick,
                price=trade.price / SIM_CONFIG.PRICE_SCALE,
                quantity=trade.quantity
            ))

        return tuple(trade_views)
