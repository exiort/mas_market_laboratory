from __future__ import annotations
from typing import Dict, Optional
import math

from market.global_vars import MarketConfig
from market.market_structures.account import Account
from market.market_structures.accountview import AccountView
from market.market_structures.order import Order, OrderLifecycle, OrderEndReasons, OrderType, Side
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

    
    def register_account(self, agent_id:int, initial_cash:float=0.0, initial_shares:int=0) -> AccountView:
        assert agent_id not in self.accounts
        assert initial_cash >= 0
        assert initial_shares >= 0
        
        account = Account(
            self.__get_account_id(),
            agent_id,
            int(initial_cash * MarketConfig.PRICE_SCALE),
            initial_shares
        )

        self.accounts[agent_id] = account

        return account.create_view()


    def is_account_exist(self, agent_id:int) -> bool:
        return agent_id in self.accounts


    def limit_check_and_reserve_funds(self, order:Order) -> bool:
        # Expectations:
        # 1-agent_exist
        # 2-order_type = Limit
        # 3-price != None && price > 0
        # 4-quantity > 0
        # 5-remaining_quantity = quantity
        # 6-lifecycle = WORKING
        # 7-end_reason = NONE
        # 8-average_trade_price = None
        # 9-trades = {}
        
        assert order.order_type == OrderType.LIMIT #2
        assert order.price is not None #3
        assert order.price > 0 #3
        assert order.quantity > 0 #4
        assert order.remaining_quantity == order.quantity #5
        assert order.lifecycle == OrderLifecycle.WORKING #6
        assert order.end_reason == OrderEndReasons.NONE #7
        assert order.average_trade_price is None #8
        assert not order.trades #9
        
        account = self.accounts.get(order.agent_id)
        assert account is not None #1
        
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

            
    def market_calculate_possible_quantities(self, order:Order, trade_price:Optional[int]=None) -> int:
        # Expectations
        # 1-agent_exist
        # 2-order_type = Market
        # 3-price = None
        # 4-quantity > 0
        # 5-0 < remaining_quantity <= quantity
        # 6-lifecycle = WORKING
        # 7-end_reason = NONE
        
        assert order.order_type == OrderType.MARKET #2 
        assert order.price is None #3
        assert order.quantity > 0
        assert 0 < order.remaining_quantity <= order.quantity
        assert order.lifecycle == OrderLifecycle.WORKING
        assert order.end_reason == OrderEndReasons.NONE
        
        account = self.accounts.get(order.agent_id)
        assert account is not None #1

        if order.side == Side.BUY:
            assert trade_price is not None
            return min(int(math.floor(account.cash / trade_price)), order.remaining_quantity)

        elif order.side == Side.SELL:
            return min(order.remaining_quantity, account.shares)
        
        else:
            assert False

            
    def release_cash(self, order:Order, account:Optional[Account]=None, traded_quantity:Optional[int]=None) -> None:
        # Expectations
        # 1-agent_exist
        # 2-order_type = Limit
        # 3-price != None && price > 0
        # 4-quantity > 0
        # 5-0 < remaining_quantity < quantity
        # 6-lifecycle = WORKING
        # 7-end_reason = NONE
        # 8-order_id in account.reserved_cash
        # 9-remaining_quantity = account.reserved_cash.quantity
        # 10-price = account.reserved_cash.price 
        # 11-traded_quantity <= reserved_quantity
        
        if account is None:
            account = self.accounts.get(order.agent_id)
            assert account is not None #1

        assert order.order_type == OrderType.LIMIT #2
        assert order.price is not None #3
        assert order.price > 0 #3
        assert order.quantity > 0 #4
        assert 0 < order.remaining_quantity <= order.quantity #5
        assert order.lifecycle == OrderLifecycle.WORKING #6
        assert order.end_reason == OrderEndReasons.NONE #7
        assert order.order_id in account.reserved_cash #8
        assert order.remaining_quantity == account.reserved_cash[order.order_id][0] #9
        assert order.price == account.reserved_cash[order.order_id][1] #10
        
        reserved_quantity, reserved_price = account.reserved_cash[order.order_id]    
        released_quantity = traded_quantity if traded_quantity is not None else reserved_quantity
        assert released_quantity <= reserved_quantity #11
        
        released_cash = released_quantity * reserved_price
        account.reserved_cash[order.order_id] = (reserved_quantity - released_quantity, reserved_price)

        if account.reserved_cash[order.order_id][0] == 0:
            del account.reserved_cash[order.order_id]

        account.cash += released_cash

        
    def release_shares(self, order:Order, account:Optional[Account]=None, traded_quantity:Optional[int]=None) -> None:
        # Expectations
        # 1-agent_exist
        # 2-order_type = Limit
        # 3-price != None && price > 0
        # 4-quantity > 0
        # 5-0 < remaining_quantity < quantity
        # 6-lifecycle = WORKING
        # 7-end_reason = NONE
        # 8-order_id in account.reserved_cash
        # 9-remaining_quantity = account.reserved_cash.quantity
        # 10 traded_quantity <= reserved_quantity
        if account is None:
            account = self.accounts.get(order.agent_id)
            assert account is not None #1

        assert order.order_type == OrderType.LIMIT #2
        assert order.price is not None #3
        assert order.price > 0 #3
        assert order.quantity > 0 #4
        assert 0 < order.remaining_quantity <= order.quantity #5
        assert order.lifecycle == OrderLifecycle.WORKING #6
        assert order.end_reason == OrderEndReasons.NONE #7
        assert order.order_id in account.reserved_shares #8
        assert order.remaining_quantity == account.reserved_shares[order.order_id] #9

        reserved_quantity = account.reserved_shares[order.order_id]
        released_quantitiy = traded_quantity if traded_quantity is not None else reserved_quantity
        assert released_quantitiy <= reserved_quantity #10
        
        account.reserved_shares[order.order_id] = reserved_quantity - released_quantitiy

        if account.reserved_shares[order.order_id] == 0:
            del account.reserved_shares[order.order_id]

        account.shares += released_quantitiy

        
    def settle_trade(self, buyer_order:Order, seller_order:Order, trade:Trade) -> None:
        #Expectations (buyer_order / seller_order)
        # 1-agent_exist / agent_exist
        # 2-side = Buy / side = Sell
        # 3-quantity > 0 / quantity > 0
        # 4-remaining_quantity >= trade_quantity / remaining_quantity >= trade_quantity
        # 5-If price != None -> price >= trade_price / If price != None -> price <= trade_price
        # 6-lifecycle = WORKING / lifecycle = WORKING
        # 7-end_reason = NONE / end_reason = NONE
        # (Trade)
        # 8-trade.buyer_agent_id = buyer_order.agent_id
        # 9-trade.seller_agent_id = seller_order.agent_id
        # 10-trade.buy_order_id = buyer_order.order_id
        # 11-trade.sell_order_id = seller_order.order_id
        # 12-price > 0
        # 13-quantity > 0

        buyer_account = self.accounts.get(buyer_order.agent_id)
        seller_account = self.accounts.get(seller_order.agent_id)
        assert buyer_account is not None #1
        assert seller_account is not None #1

        assert buyer_order.side == Side.BUY and seller_order.side == Side.SELL #2
        assert buyer_order.quantity > 0 and seller_order.quantity > 0 #3
        assert buyer_order.remaining_quantity >= trade.quantity and seller_order.remaining_quantity >= trade.quantity#4
        if buyer_order.price: assert buyer_order.price >= trade.price #5
        if seller_order.price: assert seller_order.price <= trade.price #5
        assert buyer_order.lifecycle == OrderLifecycle.WORKING and seller_order.lifecycle == OrderLifecycle.WORKING #6
        assert buyer_order.end_reason == OrderEndReasons.NONE and seller_order.end_reason == OrderEndReasons.NONE #7
        assert trade.buyer_agent_id == buyer_order.agent_id #8
        assert trade.seller_agent_id == seller_order.agent_id #9
        assert trade.buy_order_id == buyer_order.order_id #10
        assert trade.sell_order_id == seller_order.order_id # 11
        assert trade.price > 0 #12
        assert trade.quantity > 0 #13
        
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

        order.average_trade_price = int(price_sum / total_quantity)
