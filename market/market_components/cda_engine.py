from __future__ import annotations
from typing import Callable, Dict, Optional, Tuple, Deque
from sortedcontainers import SortedDict
from collections import deque
import time


from market.market_components.exchange_ledger import ExchangeLedger
from market.market_components.storage_ledger import StorageLedger
from market.market_structures.order import Order, OrderType, Side, OrderStatus
from market.market_structures.trade import Trade



class OrderBook:
    bids:SortedDict[float, Deque[Order]]
    asks:SortedDict[float, Deque[Order]]

    order_map:Dict[int, Order] #OrderID -> Order


    def __init__(self) -> None:
        self.__create_clean_book()

        
    def __create_clean_book(self) -> None:
        bid_sort_key_fn:Callable[[float], float] = lambda k: -k
        self.bids = SortedDict(bid_sort_key_fn)
        self.asks = SortedDict()
        self.order_map = {}
        

    def is_order_exist(self, order_id:int) -> bool:
        return order_id in self.order_map

    
    def add_order(self, order:Order) -> bool:
        assert order.order_type == OrderType.LIMIT
        assert order.price is not None #Only Limit Orders
        
        if self.is_order_exist(order.order_id):
            return False

        self.order_map[order.order_id] = order

        target_book = self.bids if order.side == Side.BUY else self.asks
        price_key = order.price if order.side == Side.SELL else -order.price

        if price_key not in target_book:
            target_book[price_key] = deque()

        target_book[price_key].append(order)
        
        return True

    
    def remove_order(self, order_id:int) -> Optional[Order]:
        if not self.is_order_exist(order_id):
            return None

        order = self.order_map.pop(order_id)

        assert order.order_type == OrderType.LIMIT
        assert order.price is not None

        target_book = self.bids if order.side == Side.BUY else self.asks
        price_key = order.price if order.side == Side.SELL else -order.price

        target_book[price_key].remove(order)

        if not target_book[price_key]:
            del target_book[price_key]

        return order
        

    def expire_book(self) -> Optional[Tuple[Tuple[Order, ...], Tuple[Order, ...]]]:
        if not self.order_map:
            return None
        
        bids = [order for level_queue in self.bids.values() for order in level_queue]
        asks = [order for level_queue in self.asks.values() for order in level_queue]

        self.__create_clean_book()

        return tuple(bids), tuple(asks)

    
    def get_best_bid(self) -> Optional[float]:
        if not self.bids:
            return None

        return self.bids.keys()[0]

    
    def get_best_ask_price(self) -> Optional[float]:
        if not self.asks:
            return None

        return self.asks.keys()[0]


    def get_best_bid_order(self) -> Optional[Order]:
        if not self.bids:
            return None

        return self.bids.peekitem(0)[1][0]
    
    def get_best_ask_order(self) -> Optional[Order]:
        if not self.asks:
            return None

        return self.asks.peekitem(0)[1][0]

    
    def get_best_bid_queue(self) -> Optional[Deque[Order]]:
        if not self.bids:
            return None

        return self.bids.peekitem(0)[1]

    
    def get_best_ask_queue(self) -> Optional[Deque[Order]]:
        if not self.asks:
            return None
        
        return self.asks.peekitem(0)[1]

    

class CDAEngine:
    macro_tick:int
    micro_tick:int
    
    order_book:OrderBook
    storage_ledger:StorageLedger
    exchange_ledger:ExchangeLedger

    __next_trade_id:int
    
    def __init__(self, macro_tick:int, micro_tick:int, storage_ledger:StorageLedger, exchange_ledger:ExchangeLedger) -> None:
        self.macro_tick = macro_tick
        self.micro_tick = micro_tick
        
        self.storage_ledger = storage_ledger
        self.exchange_ledger = exchange_ledger

        self.order_book = OrderBook()

        self.__next_trade_id = 0

        
    def __get_trade_id(self) -> int:
        trade_id = self.__next_trade_id 
        self.__next_trade_id += 1

        return trade_id


    def update_ticks(self, macro_tick:int, micro_tick:int) -> None:
        assert macro_tick >= self.macro_tick
        if macro_tick == self.macro_tick:
            assert micro_tick > self.micro_tick
            
        self.macro_tick = macro_tick
        self.micro_tick = micro_tick
    
    
    def process_new_order(self, order:Order) -> None:
        order.status = OrderStatus.OPEN
        
        if order.order_type == OrderType.LIMIT:
            self.__process_new_limit_order(order)

        elif order.order_type == OrderType.MARKET:
            self.__process_new_market_order(order)

        else:
            assert False
        

    def __process_new_limit_order(self, order:Order) -> None:
        assert order.order_type == OrderType.LIMIT
        assert order.price is not None

        is_account_available = self.exchange_ledger.check_and_reserve_limit_fund(order)
        if not is_account_available:
            order.status = OrderStatus.REJECTED
            return

        wash_trade_detected = False
        while order.remaining_quantity > 0:
            if order.side == Side.BUY:
                maker_order = self.order_book.get_best_ask_order()
                seller_order = maker_order
                if not maker_order or not seller_order:
                    break

                assert seller_order.order_type == OrderType.LIMIT
                assert seller_order.price is not None

                buyer_order = order
                assert buyer_order.order_type == OrderType.LIMIT
                assert buyer_order.price is not None

                if buyer_order.agent_id == seller_order.agent_id:
                    wash_trade_detected = True
                    break
                
                if buyer_order.price < seller_order.price:
                    break

                trade_price = seller_order.price
                
            elif order.side == Side.SELL:
                maker_order = self.order_book.get_best_bid_order()
                buyer_order = maker_order
                if not maker_order or not buyer_order:
                    break

                assert buyer_order.order_type == OrderType.LIMIT
                assert buyer_order.price is not None

                seller_order = order
                assert seller_order.order_type == OrderType.LIMIT
                assert seller_order.price is not None

                if buyer_order.agent_id == seller_order.agent_id:
                    wash_trade_detected = True
                    break
                
                if buyer_order.price < seller_order.price:
                    break

                trade_price = buyer_order.price
                
            else:
                assert False

            trade_quantitiy = min(buyer_order.remaining_quantity, seller_order.remaining_quantity)

            trade = Trade(
                trade_id=self.__get_trade_id(),
                timestamp=time.time(),
                macro_tick=self.macro_tick,
                micro_tick=self.micro_tick,
                seller_agent_id=seller_order.agent_id,
                sell_order_id=seller_order.order_id,
                buyer_agent_id=buyer_order.agent_id,
                buy_order_id=buyer_order.order_id,
                price=trade_price,
                quantity=trade_quantitiy
            )

            self.__execute_trade(buyer_order, seller_order, trade)

            if maker_order.remaining_quantity == 0:
                maker_order = self.order_book.remove_order(maker_order.order_id)
                assert maker_order is not None
                maker_order.status = OrderStatus.FILLED
        
        if order.remaining_quantity == 0:
            order.status = OrderStatus.FILLED
        else:
            if wash_trade_detected:
                order.status = OrderStatus.PARTIALLY_FILLED
                return
            self.order_book.add_order(order)

            
    def __process_new_market_order(self, order:Order) -> None:
        assert order.order_type == OrderType.MARKET
        assert order.price is None

        wash_trade_detected = False
        while order.remaining_quantity > 0:
            if order.side == Side.BUY:
                maker_order = self.order_book.get_best_ask_order()
                seller_order = maker_order
                if not seller_order or not maker_order:
                    break

                assert seller_order.order_type == OrderType.LIMIT
                assert seller_order.price is not None

                buyer_order = order
                assert buyer_order.order_type == OrderType.MARKET
                assert buyer_order.price is None

                if buyer_order.agent_id == seller_order.agent_id:
                    wash_trade_detected = True
                    break
                
                trade_price = seller_order.price
                
                possible_shares = self.exchange_ledger.calculate_possible_shares(buyer_order, trade_price)
                if possible_shares == 0:
                    break
                
            elif order.side == Side.SELL:
                maker_order = self.order_book.get_best_bid_order()
                buyer_order = maker_order
                if not buyer_order or not maker_order:
                    break

                assert buyer_order.order_type == OrderType.LIMIT
                assert buyer_order.price is not None

                seller_order = order
                assert seller_order.order_type == OrderType.MARKET
                assert seller_order.price is None

                if buyer_order.agent_id == seller_order.agent_id:
                    wash_trade_detected = True
                    break
                
                trade_price = buyer_order.price
                
                possible_shares = seller_order.remaining_quantity

            else:
                assert False

            trade_quantity = min(possible_shares, maker_order.remaining_quantity)

            trade = Trade(
                trade_id=self.__get_trade_id(),
                timestamp=time.time(),
                macro_tick=self.macro_tick,
                micro_tick=self.micro_tick,
                seller_agent_id=seller_order.agent_id,
                sell_order_id=seller_order.order_id,
                buyer_agent_id=buyer_order.agent_id,
                buy_order_id=buyer_order.order_id,
                price=trade_price,
                quantity=trade_quantity
            )

            self.__execute_trade(buyer_order, seller_order, trade)

            if maker_order.remaining_quantity == 0:
                maker_order = self.order_book.remove_order(maker_order.order_id)
                assert maker_order is not None
                maker_order.status = OrderStatus.FILLED
                
        if order.remaining_quantity == 0:
            order.status = OrderStatus.FILLED
        elif order.remaining_quantity == order.quantity:
            order.status = OrderStatus.REJECTED
        else:
            order.status = OrderStatus.PARTIALLY_FILLED

            
    def __execute_trade(self, buyer_order:Order, seller_order:Order, trade:Trade) -> None:
        self.exchange_ledger.settle_trade(buyer_order, seller_order, trade)
        self.storage_ledger.add_trade(trade)
        
    
    def cancel_order(self, order_id:int) -> None:
        order = self.order_book.remove_order(order_id)
        assert order is not None
        
        if order.side == Side.BUY:
            self.exchange_ledger.release_cash(order)
        elif order.side == Side.SELL:
            self.exchange_ledger.release_shares(order)
        else:
            assert False

        order.status = OrderStatus.CANCELED

        
    def expire_session(self) -> None:
        book = self.order_book.expire_book()
        if book is None:
            return

        bids, asks = book
        
        for bid in bids:
            self.exchange_ledger.release_cash(bid)
            bid.status = OrderStatus.EXPIRED

        for ask in asks:
            self.exchange_ledger.release_shares(ask)
            ask.status = OrderStatus.EXPIRED
