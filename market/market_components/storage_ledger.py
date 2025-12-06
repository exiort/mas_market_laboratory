from __future__ import annotations
from typing import Dict

from market.market_structures.deposit import Deposit
from market.market_structures.order import Order
from market.market_structures.trade import Trade



class StorageLedger:
    macro_tick:int
    micro_tick:int

    orders:Dict[int, Order] #OrderID -> Order
    trades:Dict[int, Trade] #TradeID -> Trade
    deposits:Dict[int, Deposit] #DepositID -> Deposit


    def __init__(self, macro_tick:int, micro_tick:int) -> None:
        self.macro_tick = macro_tick
        self.micro_tick = micro_tick
        self.orders = {}
        self.trades = {}
        self.deposits = {}


    def update_ticks(self, macro_tick:int, micro_tick:int) -> None:
        assert macro_tick >= self.macro_tick
        if macro_tick == self.macro_tick:
            assert micro_tick > self.micro_tick
            
        self.macro_tick = macro_tick
        self.micro_tick = micro_tick
        

    def add_order(self, order:Order) -> bool:
        if order.order_id in self.orders:
            return False

        self.orders[order.order_id] = order
        return True

    
    def add_trade(self, trade:Trade) -> bool:
        if trade.trade_id in self.trades:
            return False

        self.trades[trade.trade_id] = trade
        return True


    def add_deposit(self, deposit:Deposit) -> bool:
        if deposit.deposit_id in self.deposits:
            return False

        self.deposits[deposit.deposit_id] = deposit
        return True


    def remove_order(self, order_id:int) -> bool:
        if order_id not in self.orders:
            return False

        del self.orders[order_id]
        return True
    
        
    def remove_trade(self, trade_id:int) -> bool:
        if trade_id not in self.trades:
            return False

        del self.trades[trade_id]
        return True


    def remove_deposit(self, deposit_id:int) -> bool:
        if deposit_id not in self.deposits:
            return False

        del self.deposits[deposit_id]
        return True


    def flush(self) -> bool:...
