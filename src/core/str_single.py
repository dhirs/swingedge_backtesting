import backtrader as bt
from src.strategies.macd_cross.strategy import BaseStrategy
# from src.strategies.bolbands.strategy import BaseStrategy
import src.core.run_test as backtest


strategy= bt.Cerebro() 
strategy.addstrategy(BaseStrategy)

asset_class = 'crypto'
symbol = 'X:BTCUSD'
timeframe = '4h'

data = backtest.get_data(timeframe,symbol,asset_class)
strategy.adddata(data)

strategy = backtest.add_analyzers(strategy)


results = strategy.run()
backtest.display_results(results,timeframe)




