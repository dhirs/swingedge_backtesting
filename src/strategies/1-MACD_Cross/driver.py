import backtrader as bt
from strategy import BaseStrategy
import src.core.run_test as backtest


def get_strategy_obj():
    strategy= bt.Cerebro() 
    strategy.optstrategy(BaseStrategy,
                        max_loss_p = range(1,4,1),
                        risk_reward = range(1,8,1)
                        )
    return strategy


def get_symbols():
    symbols = ['IBM','NVIDIA','TSLA',
               'META','AMZN','ADBE', 'INTC', 
               'MSFT','NFLX','APPL','GOOGL'] 
    
    # symbols = ['TSLA','GOOGL']
    return symbols


def run(symbol,opt_mode=1):
 
  periods = ['1h','4h','1d']
  
  run_loop_done = False
  count = 0
  
  for timeframe in periods:
    count += 1
    
    if count == len(periods):
       run_loop_done = True
       count = 0 
    
    # add new strategy instance for each timeframe
    strategy = get_strategy_obj()
    
    # add data to cerebro strategy object
    data = backtest.get_data(timeframe,symbol)
    
    # skip processing the timeframe if no data exists
    if data is None:
        continue
    strategy.adddata(data)
    
    # run backtest for each timeframe for each symbol
    backtest.getResults(symbol,strategy, timeframe,run_loop_done,opt_mode)    

if __name__ == "__main__":

    for symbol in get_symbols():
        
        run(symbol)