import backtrader as bt
from src.strategies.bolbands.strategy import BaseStrategy
import src.core.run_test as backtest

strategy= bt.Cerebro() 
strategy.addstrategy(BaseStrategy)

asset_class = 'crypto'
symbol = 'X:BTCUSD'
timeframe = '1d'

data = backtest.get_data(timeframe,symbol,asset_class)
strategy.adddata(data)

backtest.add_analyzers(strategy)

results = strategy.run()
final = backtest.collect_results(results,timeframe)
print(final)

