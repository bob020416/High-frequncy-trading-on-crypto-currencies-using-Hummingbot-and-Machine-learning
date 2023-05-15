from collections import deque
from decimal import Decimal
from hummingbot.core.data_type.common import OrderType
from hummingbot.strategy.script_strategy_base import ScriptStrategyBase
import numpy as np
import pandas as pd
import csv
import datetime
import threading
import time

class OrderBookTrading(ScriptStrategyBase):
    markets = {"binance_paper_trade": {"BTC-USDT"}}
    position = 0
    timestep = 1.0  # Fetch data every 1 second
    is_writing = False
    last_write_time = time.time()  # Initialize last write time

    def on_tick(self):
        current_time = time.time()
        if self.is_writing or current_time - self.last_write_time < self.timestep:
            return
        self.is_writing = True
    
        try:
            # Get order book data
            ob = self.connectors["binance_paper_trade"].get_order_book("BTC-USDT")
            timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
    
            # Extract data from order book
            bid_entries = list(ob.bid_entries())[:5]  # Get only top 5 bid entries
            ask_entries = list(ob.ask_entries())[:5]  # Get only top 5 ask entries
    
            for i, price_level in enumerate(bid_entries):
                price, quantity = price_level.price, price_level.amount
                self.csv_writer.writerow(["BTC-USDT", i+1, timestamp, "", i+1, price, quantity, "", "B", price, quantity])
    
            for i, price_level in enumerate(ask_entries):
                price, quantity = price_level.price, price_level.amount
                self.csv_writer.writerow(["BTC-USDT", len(bid_entries)+i+1, timestamp, "", len(bid_entries)+i+1, price, quantity, "", "A", price, quantity])
    
            # Update the last write time
            self.last_write_time = time.time()
    
        finally:
            self.is_writing = False




    def on_stop(self):
        # Add any necessary cleanup code here
        self.csv_file.close()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        self.csv_file = open(f'order_book_{timestamp}.csv', mode='w', newline='')
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(["Series", "SequenceNumber", "TimeStamp", "OrderNumber", "OrderBookPosition", "Price", "QuantityDifference", "Trade", "BidOrAsk", "BestPrice", "BestQuantity"])
