from __future__ import annotations
from typing import Dict, Optional
import math

from market.market_structures.account import Account
from market.market_structures.order import Order, OrderStatus, OrderType, Side
from market.market_structures.trade import Trade



class ExchangeLedger:
    accounts:Dict[int, Account] #AgentID -> Account

    __next_account_id:int

    
    def __init__(self) -> None:
        self.accounts = {}
        self.__next_account_id = 0


    def __get_account_id(self) -> int:
        account_id = self.__next_account_id
        self.__next_account_id += 1

        return account_id

    
    def register_account(self, agent_id:int, initial_cash:float, initial_shares:int):
        assert agent_id not in self.accounts

        account = Account(
            self.__get_account_id(),
            agent_id,
            initial_cash,
            initial_shares
        )

        self.accounts[agent_id] = account
        ### ADD MECHANISM TO LET AGENT KNOW


    def is_account_exist(self, agent_id:int) -> bool:
        return agent_id in self.accounts


    def check_and_reserve_limit_fund(self, order:Order) -> bool:
        assert order.status == OrderStatus.OPEN
        assert order.order_type == OrderType.LIMIT
        assert order.price is not None
        
        account = self.accounts.get(order.agent_id)
        assert account is not None
        
        if order.side == Side.BUY:
            required_cash = order.quantity * order.price

            if account.cash < required_cash:
                return False

            account.reserved_cash[order.order_id] = (order.quantity, order.price)
            account.cash -= required_cash
            return True
            
        elif order.side == Side.SELL:
            required_shares = order.quantity

            if account.shares < required_shares:
                return False

            account.reserved_shares[order.order_id] = order.quantity
            account.shares -= required_shares
            return True
        
        else:
            assert False

            
    def calculate_possible_shares(self, buyer_order:Order, trade_price:float) -> int:
        assert buyer_order.order_type == OrderType.MARKET
        assert buyer_order.price is None

        buyer_account = self.accounts.get(buyer_order.agent_id)
        assert buyer_account is not None

        return min(math.floor(buyer_account.cash / trade_price), buyer_order.remaining_quantity)
        

    def release_cash(self, order:Order, account:Optional[Account]=None, traded_quantity:Optional[int]=None) -> None:
        if account is None:
            account = self.accounts.get(order.agent_id)
            assert account is not None

        assert order.order_type == OrderType.LIMIT
        assert order.price is not None
        assert order.order_id in account.reserved_cash
        assert order.remaining_quantity == account.reserved_cash[order.order_id][0]
        assert order.price == account.reserved_cash[order.order_id][1]

        reserved_quantity, reserved_price = account.reserved_cash[order.order_id]    
        released_quantity = traded_quantity if traded_quantity is not None else reserved_quantity
        assert released_quantity <= reserved_quantity
        
        released_cash = released_quantity * reserved_price
        account.reserved_cash[order.order_id] = (reserved_quantity - released_quantity, reserved_price)

        if account.reserved_cash[order.order_id][0] == 0:
            del account.reserved_cash[order.order_id]

        account.cash += released_cash

        
    def release_shares(self, order:Order, account:Optional[Account]=None, traded_quantity:Optional[int]=None) -> None:
        if account is None:
            account = self.accounts.get(order.agent_id)
            assert account is not None

        assert order.order_type == OrderType.LIMIT
        assert order.price is not None
        assert order.order_id in account.reserved_shares
        assert order.remaining_quantity == account.reserved_shares[order.order_id]

        reserved_quantity = account.reserved_shares[order.order_id]
        released_quantitiy = traded_quantity if traded_quantity is not None else reserved_quantity
        assert released_quantitiy <= reserved_quantity
        
        account.reserved_shares[order.order_id] = reserved_quantity - released_quantitiy

        if account.reserved_shares[order.order_id] == 0:
            del account.reserved_shares[order.order_id]

        account.shares += released_quantitiy

        
    def settle_trade(self, buyer_order:Order, seller_order:Order, trade:Trade) -> None:
        buyer_account = self.accounts.get(buyer_order.agent_id)
        seller_account = self.accounts.get(seller_order.agent_id)
        assert buyer_account is not None
        assert seller_account is not None

        if buyer_order.order_type == OrderType.LIMIT:
            self.release_cash(buyer_order, buyer_account, trade.quantity)
        
        if seller_order.order_type == OrderType.LIMIT:
            self.release_shares(seller_order, seller_account, trade.quantity)
            
        trade_cost = trade.quantity * trade.price

        buyer_account.cash -= trade_cost
        buyer_account.shares += trade.quantity

        seller_account.cash += trade_cost
        seller_account.shares -= trade.quantity

        assert buyer_account.cash >= 0.0
        assert seller_account.shares >= 0

        buyer_order.remaining_quantity -= trade.quantity
        seller_order.remaining_quantity -= trade.quantity
        
        buyer_order.trades[trade.trade_id] = trade
        seller_order.trades[trade.trade_id] = trade

        self.__update_avarage_trade_price(buyer_order)
        self.__update_avarage_trade_price(seller_order)

        
    def __update_avarage_trade_price(self, order:Order):
        if not order.trades:
            return

        total_quantity = 0
        price_sum = 0

        for trade in order.trades.values():
            total_quantity += trade.quantity
            price_sum += trade.price * trade.quantity

        order.avarage_trade_price = price_sum / total_quantity
