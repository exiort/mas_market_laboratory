from __future__ import annotations
from typing import Optional
import time

from market.market_components.exchange_ledger import ExchangeLedger
from market.market_components.cda_engine import CDAEngine
from market.market_components.storage_ledger import StorageLedger
from market.market_structures.order import Order, OrderStatus, Side, OrderType



class Market:
    macro_tick:int
    micro_tick:int
    
    exchange_ledger:ExchangeLedger
    cda_engine:CDAEngine
    storage_ledger:StorageLedger

    _next_order_id:int
    
    
    def __init__(self, macro_tick:int, micro_tick:int) -> None:
        self.macro_tick = macro_tick
        self.micro_tick = micro_tick
        
        self.storage_ledger = StorageLedger(
            macro_tick=macro_tick,
            micro_tick=micro_tick
        )
        self.exchange_ledger = ExchangeLedger()
        self.cda_engine = CDAEngine(
            macro_tick=macro_tick,
            micro_tick=micro_tick,
            storage_ledger=self.storage_ledger,
            exchange_ledger=self.exchange_ledger
        )

        self._next_order_id = 0
        

    def __get_order_id(self) -> int:
        order_id = self._next_order_id
        self._next_order_id += 1

        return order_id
    
        
    def update_ticks(self, macro_tick:int, micro_tick:int) -> None:
        assert macro_tick >= self.macro_tick
        if macro_tick == self.macro_tick:
            assert micro_tick > self.micro_tick
        
        self.macro_tick = macro_tick
        self.micro_tick = micro_tick

        self.storage_ledger.update_ticks(macro_tick, micro_tick)
        self.cda_engine.update_ticks(macro_tick, micro_tick)


    def create_order(
            self,
            agent_id:int,
            order_type:OrderType,
            side:Side,
            quantity:int,
            price:Optional[float] = None
    ):
        if not self.exchange_ledger.is_account_exist(agent_id):
            return
        
        if not quantity > 0:
            return

        if order_type == OrderType.LIMIT:
            if price is None or price <= 0:
                return

        elif order_type == OrderType.MARKET:
            if price is not None:
                return

        order = Order(
            order_id=self.__get_order_id(),
            agent_id=agent_id,
            timestamp=time.time(),
            macro_tick=self.macro_tick,
            micro_tick=self.micro_tick,
            order_type=order_type,
            side=side,
            quantity=quantity,
            price=price,
            status=OrderStatus.PENDING,
            avarage_trade_price=-1
        )

        self.cda_engine.process_new_order(order)

