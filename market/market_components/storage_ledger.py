from __future__ import annotations
from typing import Dict, Optional

from market.market_structures.deposit import Deposit
from market.market_structures.order import Order
from market.market_structures.trade import Trade



class StorageLedger:
    orders:Dict[int, Order] #OrderID -> Order
    trades:Dict[int, Trade] #TradeID -> Trade
    deposits:Dict[int, Deposit] #DepositID -> Deposit


    def __init__(self) -> None:
        self.orders = {}
        self.trades = {}
        self.deposits = {}
        

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

    
    def get_order(self, order_id:int) -> Optional[Order]:
        return self.orders.get(order_id)

    
    def get_trade(self, trade_id:int) -> Optional[Trade]:
        return self.trades.get(trade_id)


    def get_deposit(self, deposit_id:int) -> Optional[Deposit]:
        return self.deposits.get(deposit_id)
    
    
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
