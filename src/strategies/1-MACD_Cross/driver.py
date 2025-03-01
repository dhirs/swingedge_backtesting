import backtrader as bt
from strategy import BaseStrategy
import src.core.run_test as backtest
from src.core.db import Database as db

def get_strategy_obj():
    strategy= bt.Cerebro() 
    strategy.optstrategy(BaseStrategy,
                        max_loss_p = range(1,4,1),
                        risk_reward = range(1,8,1)
                        )
    return strategy


def get_symbols():
    # symbols_list = ['FAST']
    try:
        
        index = 'N100'
        query = f"select symbol from instrument_index where index_f = '{index}';"
        database = db()
        symbols_df = database.get_data_frame(query)
        symbols_list = symbols_df['symbol'].tolist()
        
    except Exception as err:
        print(f"!!!!!!!No symbols found for given query!!!!!!!!!!{err}")
        
    
    return symbols_list


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

    symbols = get_symbols()
    if not symbols:
        exit()
    
    for symbol in get_symbols():
        
        print(f"----Starting run for {symbol}-----")
        try:
            run(symbol)
            print(f"----Completed run for {symbol}-----")
        except Exception as e:
            print(f"!!!!!!Error completing run for {symbol}!!!!!!!!!")
            continue