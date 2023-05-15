#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  4 17:46:29 2023

@author: user
"""
import pandas as pd
import numpy as np

data = pd.read_csv('/Users/user/Downloads/tick_data4_20.csv', sep=',')

lookback_window = 50


data['ratio_moving_average'] = data['ratio'].rolling(window=lookback_window).mean()
data['ratio_std'] = data['ratio'].rolling(window=lookback_window).std()

data['zscore'] = (data['ratio'] - data['ratio_moving_average']) / data['ratio_std']
data['zscore_rate_of_change'] = data['zscore'].diff()


zscore_threshold = 0.9

roc_threshold = 0.005

data['long_entry'] = (data['zscore_rate_of_change'] > roc_threshold) & (data['zscore'] < -zscore_threshold)
data['short_entry'] = (data['zscore_rate_of_change'] < -roc_threshold) & (data['zscore'] > zscore_threshold)
data['exit'] = (data['zscore'] > -zscore_threshold) & (data['zscore'] < zscore_threshold)

data['position'] = 0
data['btc_returns'] = 0
data['ada_returns'] = 0

position = 0

for index, row in data.iterrows():
    if row['long_entry'] and position == 0:
        position = 1
    elif row['short_entry'] and position == 0:
        position = -1
    elif row['exit']:
        position = 0

    if position != 0:
        data.loc[index, 'btc_returns'] = (row['BTC-USDT'] / data.loc[index - 1, 'BTC-USDT'] - 1) * -position
        data.loc[index, 'ada_returns'] = (row['ADA-USDT'] / data.loc[index - 1, 'ADA-USDT'] - 1) * position

    data.loc[index, 'position'] = position

data['cumulative_btc_returns'] = (data['btc_returns'] + 1).cumprod()
data['cumulative_ada_returns'] = (data['ada_returns'] + 1).cumprod()

data['average_returns'] = (data['btc_returns'] + data['ada_returns']) / 2
data['cumulative_average_returns'] = (data['average_returns'] + 1).cumprod()

average_daily_return = data['average_returns'].mean()
daily_std = data['average_returns'].std()
sharpe_ratio = average_daily_return / daily_std * np.sqrt(252)

# Calculate the overall return
overall_return = data['cumulative_average_returns'].iloc[-1] - 1
# Calculate the overall return

print(overall_return)

