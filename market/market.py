from __future__ import annotations
from typing import Optional
import time

from market.global_vars import MarketConfig, HYBRID_TIME
from market.market_components.exchange_ledger import ExchangeLedger
from market.market_components.cda_engine import CDAEngine
from market.market_components.storage_ledger import StorageLedger
from market.market_structures.accountview import AccountView
from market.market_structures.order import Order, OrderLifecycle, OrderEndReasons, Side, OrderType
from market.market_structures.orderview import OrderView



class Market:
    exchange_ledger:ExchangeLedger
    cda_engine:CDAEngine
    storage_ledger:StorageLedger

    _next_order_id:int
    
    
    def __init__(self) -> None:      
        self.storage_ledger = StorageLedger()
        self.exchange_ledger = ExchangeLedger()
        self.cda_engine = CDAEngine(
            storage_ledger=self.storage_ledger,
            exchange_ledger=self.exchange_ledger
        )

        self._next_order_id = 0
        

    def __get_order_id(self) -> int:
        order_id = self._next_order_id
        self._next_order_id += 1

        return order_id

        
    def register_agent(
            self,
            agent_id:int,
            initial_cash:float=0.0,
            initial_shares:int=0
    ) -> Optional[AccountView]:
        if self.exchange_ledger.is_account_exist(agent_id): return
        if initial_cash < 0: return
        if initial_shares < 0: return

        return self.exchange_ledger.register_account(
            agent_id=agent_id,
            initial_cash=initial_cash,
            initial_shares=initial_shares
        )
        
    
    def create_order(
            self,
            agent_id:int,
            order_type:OrderType,
            side:Side,
            quantity:int,
            price:Optional[float]=None
    ) -> Optional[OrderView]:
        if not self.exchange_ledger.is_account_exist(agent_id):
            return

        if not quantity > 0:
            return

        if order_type == OrderType.LIMIT:
            if price is None or price <= 0:
                return
            price = int(price * MarketConfig.PRICE_SCALE)
            
        elif order_type == OrderType.MARKET:
            if price is not None:
                return

        order = Order(
            order_id=self.__get_order_id(),
            agent_id=agent_id,
            timestamp=time.time(),
            macro_tick=HYBRID_TIME.MACRO_TICK,
            micro_tick=HYBRID_TIME.MICRO_TICK,
            order_type=order_type,
            side=side,
            quantity=quantity,
            price=price,
            lifecycle=OrderLifecycle.NEW,
            end_reason=OrderEndReasons.NONE
        )

        if not self.storage_ledger.add_order(order):
            return
        
        self.cda_engine.process_new_order(order)
        
        return order.create_view()


    def cancel_order(self, agent_id:int, order_id:int) -> None:
        if not self.exchange_ledger.is_account_exist(agent_id): return

        order = self.storage_ledger.get_order(order_id)
        if order is None: return
        if order.agent_id != agent_id: return
        if order.lifecycle != OrderLifecycle.WORKING: return
        if order.end_reason != OrderEndReasons.NONE: return
        
        self.cda_engine.cancel_order(order_id)
        

    def expire_session(self) -> None:
        self.cda_engine.expire_session()
