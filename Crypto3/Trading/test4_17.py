#!/usr/bin/env python3
from collections import deque
from decimal import Decimal
from statistics import mean
from hummingbot.core.data_type.common import OrderType
from hummingbot.strategy.script_strategy_base import ScriptStrategyBase
import numpy as np
import pandas as pd
import csv
from datetime import datetime


class buyLowSellHigh(ScriptStrategyBase):
    markets = {"gate_io_paper_trade": {"BTC-USDT","ADA-USDT"}}
    #: pingpong is a variable to allow alternating between buy & sell signals

    """
    for the sake of simplicity in testing, we will define fast MA as the 5-secondly-MA, and slow MA as the
    20-secondly-MA. User can change this as desired
    """
    prev_zscore = 0
    
    de_fast_ma = deque([], maxlen=200)
    de_slow_ma = deque([], maxlen=2000)
    
    # Define the entry and exit thresholds
    entry_threshold = 2.0
    exit_threshold = 1
    entry_price_ada = 0  # Track the entry price for ADA trades
    
    # Add entry_price variables to track the entry prices for each position
    entry_price_1 = 0
    entry_price_2 = 0

    
    # Implement the trading strategy
    position = 0
    
    
    #Define trade amount 
    trade_amount_btc = Decimal(0.01)

    

    
    
    def on_tick(self):
        p1 = self.connectors["gate_io_paper_trade"].get_price("BTC-USDT", True)
        p2 = self.connectors["gate_io_paper_trade"].get_price("ADA-USDT", True)
        ratio = p1/p2
    
        trade_amount_ada = Decimal(100) # Calculate the equivalent ADA amount
        
        #: with every tick, the new price of the trading_pair will be appended to the deque and MA will be calculated
        self.de_fast_ma.append(ratio)
        self.de_slow_ma.append(ratio)
        
        fast_ma = mean(self.de_fast_ma)
        slow_ma = mean(self.de_slow_ma)
        std_ma = np.std((self.de_slow_ma))
        
        zscore_60_20 = (fast_ma - slow_ma)/std_ma
        
        #For record profit in csv 
        profit_1 = (p2 - self.entry_price_1) / self.entry_price_1 if self.entry_price_1 != 0 else 0

        profit_2 = (self.entry_price_2 - p2) / self.entry_price_2 if self.entry_price_2 != 0 else 0
        

        # Write the tick data, Z-score, and profits to the CSV file
        self.csv_writer.writerow([self.current_timestamp, p1, p2, ratio, zscore_60_20, profit_1, profit_2])  
        
        if self.position == 0:
            if zscore_60_20 > self.entry_threshold and self.prev_zscore > zscore_60_20:
                
                # Store the current ratio as the entry price for position 1
                self.entry_price_1 = p2
                
            # Buy ADA and sell BTC
                self.position = 1
                self.buy(
                    connector_name="gate_io_paper_trade",
                    trading_pair="ADA-USDT",
                    amount=trade_amount_ada,
                    order_type=OrderType.MARKET,
                )
                self.logger().info(f'{"Same amount ADA bought"}')
                self.logger().info(f'{"BTC-USDT price: "}{p1}')
                self.logger().info(f'{"ADA-USDT price: "}{p2}')
                
     
                
            elif zscore_60_20 < -self.entry_threshold and self.prev_zscore < zscore_60_20:
                
                
                # Store the current ratio as the entry price for position 2
                self.entry_price_2 = p2
            # Buy BTC and sell XRP
                self.position = 2
                self.sell(
                    connector_name="gate_io_paper_trade",
                    trading_pair="ADA-USDT",
                    amount=trade_amount_ada,
                    order_type=OrderType.MARKET,
                )
                self.logger().info(f'{"Same amount ADA sold"}')
                self.logger().info(f'{"BTC-USDT price: "}{p1}')
                self.logger().info(f'{"ADA-USDT price: "}{p2}')
                
            else:
                self.logger().info(print(zscore_60_20))
                self.logger().info(f'{"wait for a signal to be generated"}')
                self.logger().info(f'{"BTC-USDT price: "}{p1}')
                self.logger().info(f'{"ADA-USDT price: "}{p2}')
                
        
        elif self.position == 1:
                            
            profit_1 = (p2 - self.entry_price_1) / self.entry_price_1
            
            if abs(zscore_60_20) < self.exit_threshold and  profit_1 > 0.004:
            # Close the position
                self.position = 0
                self.sell(
                    connector_name="gate_io_paper_trade",
                    trading_pair="ADA-USDT",
                    amount=trade_amount_ada,
                    order_type=OrderType.MARKET,
                )
                self.logger().info(f'{"Same amount ADA sold"}')
                self.logger().info(f'{"BTC-USDT price: "}{p1}')
                self.logger().info(f'{"ADA-USDT price: "}{p2}')
                
            elif profit_1 < -0.004:
                # Implement stop loss for position 1
                self.position = 0
                self.sell(
                    connector_name="gate_io_paper_trade",
                    trading_pair="ADA-USDT",
                    amount=trade_amount_ada,
                    order_type=OrderType.MARKET,
                )
                self.logger().info(f'{"Stop loss triggered: Same amount ADA sold"}')
                self.logger().info(f'{"BTC-USDT price: "}{p1}')
                self.logger().info(f'{"ADA-USDT price: "}{p2}')
                
        elif self.position == 2:
            
            profit_2 = (self.entry_price_2 - p2) / self.entry_price_2
            
            if abs(zscore_60_20) < self.exit_threshold and profit_2 > 0.004:
            # Close the position
                self.position = 0
                
                self.buy(
                    connector_name="gate_io_paper_trade",
                    trading_pair="ADA-USDT",
                    amount=trade_amount_ada,
                    order_type=OrderType.MARKET,
                )
                self.logger().info(f'{"Same amount ADA bought"}')
                self.logger().info(f'{"BTC-USDT price: "}{p1}')
                self.logger().info(f'{"ADA-USDT price: "}{p2}')
                
            elif profit_2 < -0.004:
                # Implement stop loss for position 2
                self.position = 0
                
                self.buy(
                    connector_name="gate_io_paper_trade",
                    trading_pair="ADA-USDT",
                    amount=trade_amount_ada,
                    order_type=OrderType.MARKET,
                )
                self.logger().info(f'{"Stop loss triggered: Same amount ADA bought"}')
                self.logger().info(f'{"BTC-USDT price: "}{p1}')
                self.logger().info(f'{"ADA-USDT price: "}{p2}')

        self.prev_zscore = zscore_60_20       
                
    def on_stop(self):
    # Close the CSV file when the bot is stopped
        self.csv_file.close()
    
    # For record data purpose
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.csv_file = open("tick_data.csv", mode="w", newline="")
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(["timestamp", "BTC-USDT", "ADA-USDT", "ratio", "zscore", "profit_1", "profit_2"])  


