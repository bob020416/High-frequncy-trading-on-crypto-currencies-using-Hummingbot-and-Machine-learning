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

data_points_per_hour = 3600  # Replace this value with the actual number of data points per hour
waiting_hours = 3
waiting_data_points = data_points_per_hour * waiting_hours

# Initialize data['ratio_moving_average'] and data['ratio_std'] as NaN
data['ratio_moving_average'] = np.nan
data['ratio_std'] = np.nan


# Loop through the dataset, starting from the waiting_data_points + lookback_window-th row
for index in range(waiting_data_points + lookback_window, len(data)):
    # Update the moving average and standard deviation for the current row
    data.loc[index, 'ratio_moving_average'] = data.loc[index - lookback_window:index - 1, 'ratio'].mean()
    data.loc[index, 'ratio_std'] = data.loc[index - lookback_window:index - 1, 'ratio'].std()

    # Update the z-score for the current row
    data.loc[index, 'zscore'] = (data.loc[index, 'ratio'] - data.loc[index, 'ratio_moving_average']) / data.loc[index, 'ratio_std']
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


print(overall_return)
df = pd.DataFrame(data)
df.to_csv('backtest_data.csv', index=False)

