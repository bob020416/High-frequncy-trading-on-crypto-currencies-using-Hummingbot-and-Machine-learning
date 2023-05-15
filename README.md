# High-frequncy-trading-on-crypto-currencies-using-Hummingbot-and-Machine-learning
Apply data scrapping skill on high frequncy market of crypto currencies and define trading algorithm using Hummingbot and machine learning for backtesting
大學專題 (ongoing) 

指導教授 清大資工 - 孫宏民

What is Order book trading ?
https://github.com/rorysroes/SGX-Full-OrderBook-Tick-Data-Trading-Strategy/tree/

This is a project using hummingbot interface with docker and linux
Please install hummingbot interface to run this project include 2 part : 1. short time price prediction 2. Real time HFT arbitrage 
https://hummingbot.org/



高頻交易做市假設
https://zhuanlan.zhihu.com/p/74919481
这个假设很有意思，当做市商在有信息发布时会拉大spread，愿意付出高额成本持有单子的人，只能是rookie或者拥有信息优势者(至少能保证cover这个spread)，然后做市商系统发现受伤后又近一步拉高spread或者上移ask，导致瞬时价差发生巨幅的上涨



Part 1 : 交易策略 
https://zhuanlan.zhihu.com/p/89790180

https://www.fmz.com/strategy/392321

https://blog.csdn.net/zk168_net/article/details/106252130

https://www.fmz.com/robot/513135

https://zhuanlan.zhihu.com/p/562321197

Trading logic : 

This script trades on the Binance perpetual testnet with the trading pairs you specified: "LINK-USDT", "XMR-USDT", "OCEAN-USDT", "LTC-USDT", "ATOM-USDT", "ENS-USDT", "SUSHI-USDT". 


 the bot fetches this candlestick data every three minutes for each trading pair. The `get_candles_with_features` function fetches the data and then calculates two important technical indicators:

    - **Relative Strength Index (RSI):** RSI is a momentum indicator that measures the speed and change of price movements. It oscillates between zero and 100 and is often used to identify overbought and oversold conditions in a market. In this strategy, the RSI is calculated over 14 periods.
  
    - **Normalized Average True Range (NATR):** The Average True Range (ATR) is a measure of market volatility. The NATR is simply the ATR expressed as a percentage of the closing price, which allows for comparison across different securities and market conditions. In this strategy, the NATR is calculated over 14 periods and is then halved (scalar=0.5).

2. **Multipliers Update:** After calculating the RSI and NATR, the bot uses these values to compute two multipliers for each trading pair:

    - **Price Multiplier:** This is calculated as `(50 - RSI) / 50 * NATR`. The effect of this formula is to increase the price multiplier when the RSI is low (indicating an oversold market) and the NATR is high (indicating high volatility), and to decrease the price multiplier when the RSI is high (indicating an overbought market) and the NATR is low (indicating low volatility).

    - **Spread Multiplier:** This is calculated as `NATR / spread_base`. The effect of this formula is to increase the spread multiplier when the NATR is high (indicating high volatility) and to decrease the spread multiplier when the NATR is low (indicating low volatility).

    The `update_multipliers` function calculates these multipliers and then checks whether the spread multiplier is above a certain threshold (0.02). If it is, the bot reduces the order refresh time to 10 seconds, meaning orders will be placed more frequently. Otherwise, the order refresh time is set to the default 15 seconds.

3. **Order Proposal:** After updating the multipliers, the bot creates proposals for buy and sell orders for each trading pair. The `create_proposal` function does this by first getting the mid-price (the average of the highest bid and the lowest ask prices) for each trading pair. It then adjusts this mid-price by adding the price multiplier, to give a reference price. The buy price is set to this reference price minus an amount based on the spread (which has been adjusted by the spread multiplier), while the sell price is set to the reference price plus an amount based on the spread. This ensures that the bot will aim to buy low and sell high, with the spread representing the profit margin.


Example : 

Let's say we're trading the LINK-USDT pair. 

1. **Candlestick Data:** First, the bot fetches the latest 3-minute candlestick data for LINK-USDT from Binance. Let's say the data shows high volatility (indicated by large candlestick bodies and wicks) and the price has been dropping (indicated by a series of red or down candlesticks). 

    The bot calculates the 14-period RSI and NATR based on this data. Let's say the RSI is 30, indicating that LINK is potentially oversold, and the NATR is 2%, indicating high volatility.

2. **Multipliers Update:** The bot then calculates the price and spread multipliers. 

    - The price multiplier is `(50 - 30) / 50 * 2% = 0.02`, which increases the reference price.
  
    - The spread multiplier is `2% / 0.008 = 0.25`, which increases the spread.

    The spread multiplier is greater than 0.02, so the bot reduces the order refresh time to 10 seconds.

3. **Order Proposal:** The bot gets the mid-price for LINK-USDT, let's say it's $20. 

    - The reference price is `$20 * (1 + 0.02) = $20.40`.

    - The buy price is `$20.40 * (1 - 0.25) = $15.30`.

    - The sell price is `$20.40 * (1 + 0.25) = $25.50`.

    The bot proposes to place a limit buy order for 7 LINK at $15.30 each and a limit sell order for 7 LINK at $25.50 each.

4. **Order Placement:** The bot checks its available funds. If it has at least $107.10 in USDT (7 * $15.30), it places the buy order. If it has at least 7 LINK, it places the sell order. If it doesn't have enough funds for an order, it logs a message and doesn't place that order. 

    The bot then waits 10 seconds before fetching new candlestick data and repeating the process.

Note that in a real situation, the prices for buy and sell orders are unlikely to be so far from the mid-price, as this would mean a very wide spread. The specific values will depend on the RSI, NATR, and spread base set by the user, as well as current market conditions.

    These OrderCandidate objects are returned as a list, which represents the proposal for the orders that the bot should place during the next cycle.



Part 2 : order book 時域價格預測、volatility 預測 

https://xueqiu.com/8188497048/198528860
https://posts.careerengine.us/p/61111f811c790155b66cabd1
https://newsletter.x-mol.com/paper/1597433854546202624

One example of such a model is the Queue-Reactive model, which accommodates the empirical properties of the full order book [3]. This model can simulate the dynamics of the order book and predict its future state.

The Queue-Reactive model is a type of order book model that simulates the dynamics of the order book and predicts its future state by treating the limit order book as a Markov queuing system [1]. The model accommodates empirical properties of the full order book and the stylized facts of lower-frequency financial data.

1. Prediction: Use the trained model to predict the future state of the order book based on its current state. For example, the model might predict that the mid-price will increase in the next few seconds.

2. Trading Strategy: Based on the prediction, design a trading strategy. For example, if the model predicts an increase in the mid-price, you might place a buy order at the current mid-price, expecting to sell later at a higher price. If the model predicts a decrease, you might place a sell order, expecting to buy back later at a lower price.
