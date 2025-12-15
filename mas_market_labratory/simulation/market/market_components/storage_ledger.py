from __future__ import annotations
from typing import Dict, Optional, Tuple
import sqlite3
import json

from simulation_realtime_data import get_simulation_realtime_data
from market.market_structures.economy_insight import EconomyInsight
from market.market_structures.account import Account
from market.market_structures.deposit import Deposit
from market.market_structures.order import Order
from market.market_structures.trade import Trade



class StorageLedger:
    orders:Dict[int, Order] #OrderID -> Order
    trades:Dict[int, Trade] #TradeID -> Trade
    deposits:Dict[int, Deposit] #DepositID -> Deposit
    economy_insights:Dict[int, EconomyInsight] #macro_tick -> Deposit

    db_path:str
    connection:sqlite3.Connection

    __last_flush_macro_tick:int
    
    
    def __init__(self, db_path:str) -> None:
        self.orders = {}
        self.trades = {}
        self.deposits = {}
        self.economy_insights = {}
        self.__last_flush_macro_tick = -1
        
        self.db_path = db_path
        self.connection = sqlite3.connect(self.db_path)

        self.connection.execute("PRAGMA journal_mode=WAL;")
        self.connection.execute("PRAGMA synchronous=NORMAL;")
        self.connection.execute("PRAGMA foreign_keys = ON;")

        self.__create_sheme()

                
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

    def add_economy_insight(self, economy_insight:EconomyInsight) -> bool:
        if economy_insight.macro_tick in self.economy_insights:
            return False

        self.economy_insights[economy_insight.macro_tick] = economy_insight
        return True

    
    def get_order(self, order_id:int) -> Optional[Order]:
        return self.orders.get(order_id)

    
    def get_trade(self, trade_id:int) -> Optional[Trade]:
        return self.trades.get(trade_id)


    def get_deposit(self, deposit_id:int) -> Optional[Deposit]:
        return self.deposits.get(deposit_id)
    

    def get_economy_insight(self, macro_tick:int) -> Optional[EconomyInsight]:
        return self.economy_insights.get(macro_tick)
    
    
    def flush(self,  accounts:Tuple[Account]) -> bool:
        SIM_REALTIME_DATA = get_simulation_realtime_data()
        if self.__last_flush_macro_tick == SIM_REALTIME_DATA.MACRO_TICK:
            return False

        cursor = self.connection.cursor()
        
        for account in accounts:
            self.__record_account(cursor, account)
        
        for order in self.orders.values():
            self.__record_order(cursor, order)
        
        for trade in self.trades.values():
            self.__record_trade(cursor, trade)

        for economy_insight in self.economy_insights.values():
            self.__record_economy_insight(cursor, economy_insight)
            
        self.connection.commit()
        
        self.orders = {}
        self.trades = {}
        self.economy_insights = {}
        
        self.__last_flush_macro_tick = SIM_REALTIME_DATA.MACRO_TICK
        
        return True

    
    def close(self) -> None:
        self.connection.close()


    def __create_sheme(self) -> None:
        cursor = self.connection.cursor()
        
        self.__create_order_table(cursor)
        self.__create_trade_table(cursor)
        self.__create_account_table(cursor)
        self.__create_economy_insight_table(cursor)

        cursor.close()
        self.connection.commit()


    def __create_order_table(self, cursor:sqlite3.Cursor) -> None:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY,
            agent_id INTEGER  NOT NULL,

            timestamp REAL NOT NULL,
            macro_tick INTEGER NOT NULL,
            micro_tick INTEGER NOT NULL,

            order_type TEXT NOT NULL,
            side TEXT NOT NULL,

            quantity INTEGER NOT NULL,
            price INTEGER,

            lifecycle TEXT NOT NULL,
            end_reason TEXT NOT NULL,

            remaining_quantity INTEGER NOT NULL,

            average_trade_price INTEGER
            );
            """
        )

        
    def __create_trade_table(self, cursor:sqlite3.Cursor) -> None:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS trades (
            trade_id INTEGER PRIMARY KEY,
            timestamp  REAL NOT NULL,
            macro_tick INTEGER NOT NULL,
            micro_tick INTEGER NOT NULL,

            buyer_agent_id INTEGER NOT NULL,
            buy_order_id INTEGER NOT NULL,
            seller_agent_id INTEGER NOT NULL,
            sell_order_id INTEGER NOT NULL,

            price INTEGER NOT NULL,
            quantity INTEGER NOT NULL
            );
            """
        )


    def __create_account_table(self, cursor:sqlite3.Cursor) -> None:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS accounts (
            macro_tick INTEGER NOT NULL,
            account_id INTEGER NOT NULL,
            agent_id INTEGER NOT NULL,

            cash INTEGER NOT NULL,
            shares INTEGER NOT NULL,

            reserved_cash INTEGER NOT NULL,
            reserved_shares INTEGER NOT NULL,
            deposited_cash INTEGER NOT NULL,

            PRIMARY KEY (macro_tick, account_id)
            );
            """
        )        


    def __create_economy_insight_table(self, cursor:sqlite3.Cursor) -> None:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS economy_insight (
            macro_tick INTEGER PRIMARY KEY,
            true_value INTEGER NOT NULL,
            short_rate REAL NOT NULL,
            width REAL NOT NULL,
            tv_lower_bound INTEGER NOT NULL,
            tv_upper_bound INTEGER NOT NULL,
            deposit_rates TEXT NOT NULL
            );
            """
        )
        
        
    def __record_order(self, cursor:sqlite3.Cursor, order:Order) -> None:
        cursor.execute(
            """
            INSERT INTO orders (
            order_id,
            agent_id,
            timestamp,
            macro_tick,
            micro_tick,
            order_type,
            side,
            quantity,
            price,
            lifecycle,
            end_reason,
            remaining_quantity,
            average_trade_price
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                order.order_id,
                order.agent_id,
                order.timestamp,
                order.macro_tick,
                order.micro_tick,
                order.order_type.name,
                order.side.name,
                order.quantity,
                order.price,
                order.lifecycle.name,
                order.end_reason.name,
                order.remaining_quantity,
                order.average_trade_price
            )
        )


    def __record_trade(self, cursor:sqlite3.Cursor, trade:Trade) -> None:
        cursor.execute(
            """
            INSERT INTO trades (
            trade_id,
            timestamp,
            macro_tick,
            micro_tick,
            buyer_agent_id,
            buy_order_id,
            seller_agent_id,
            sell_order_id,
            price,
            quantity
            )
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                trade.trade_id,
                trade.timestamp,
                trade.macro_tick,
                trade.micro_tick,
                trade.buyer_agent_id,
                trade.buy_order_id,
                trade.seller_agent_id,
                trade.sell_order_id,
                trade.price,
                trade.quantity
            )
        )


    def __record_account(self, cursor:sqlite3.Cursor, account:Account) -> None:
        SIM_REALTIME_DATA = get_simulation_realtime_data()
        cursor.execute(
            """
            INSERT INTO accounts (
            macro_tick,
            account_id,
            agent_id,
            cash,
            shares,
            reserved_cash,
            reserved_shares,
            deposited_cash
            )
            VALUES(?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                SIM_REALTIME_DATA.MACRO_TICK,
                account.account_id,
                account.agent_id,
                account.cash,
                account.shares,
                account.get_total_reserved_cash(),
                account.get_total_reserved_shares(),
                account.get_total_deposited_cash()
            )
        )


    def __record_economy_insight(self, cursor:sqlite3.Cursor, economy_insight:EconomyInsight) -> None:
        cursor.execute(
            """
            INSERT INTO economy_insight (
            macro_tick,
            true_value,
            short_rate,
            width,
            tv_lower_bound,
            tv_upper_bound,
            deposit_rates
            )
            VALUES(?, ?, ?, ?, ?, ?, ?);
            """,
            (
                economy_insight.macro_tick,
                economy_insight.true_value,
                economy_insight.short_rate,
                economy_insight.width,
                economy_insight.tv_interval[0],
                economy_insight.tv_interval[1],
                json.dumps(economy_insight.deposit_rates)
            )
        )
