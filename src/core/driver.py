import backtrader as bt
# from src.strategies.macd_cross.strategy import BaseStrategy
from src.strategies.bolbands.strategy import BaseStrategy
import src.core.run_test as backtest
from src.core.db import Database as db



def get_strategy_obj(strategy_id):
    strategy= bt.Cerebro() 
    strategy.optstrategy(BaseStrategy,
                        max_loss_p = range(1,4,1),
                        risk_reward = range(1,8,1)
                        )
    strategy.id = strategy_id
    return strategy


def get_symbols(asset_class='stock'):
    
    if asset_class == "stock":
        try:
        
            index = 'N100'
            query = f"select symbol from instrument_index where index_f = '{index}';"
            database = db()
            symbols_df = database.get_data_frame(query)
            symbols_list = symbols_df['symbol'].tolist()
        
        
        except Exception as err:
            print(f"!!!!!!!No symbols found for given query!!!!!!!!!!{err}")
    
    elif asset_class == 'crypto':
        symbols_list = ['X:BTCUSD']
    
    return symbols_list


def process_symbol(symbol,strategy_id, asset_class='stock', opt_mode=1,save_mode=0):
 
  if asset_class == 'crypto':
    periods = ['15m','30m', '45m', '1h','4h','1d']
  else:
    periods = ['1h','4h','1d']
    
  run_loop_done = False
  count = 0
  
  for timeframe in periods:
    count += 1
    
    if count == len(periods):
       run_loop_done = True
       count = 0 
    
    # add new strategy instance for each timeframe
    strategy = get_strategy_obj(strategy_id)
    
    # add data to cerebro strategy object
    data = backtest.get_data(timeframe,symbol,asset_class)
    
    # skip processing the timeframe if no data exists
    if data is None:
        continue
    strategy.adddata(data)
    
    # run backtest for each timeframe for each symbol
    backtest.getResults(symbol,strategy, timeframe,run_loop_done,opt_mode,save_mode)    


def run_backtest(asset_class,strategy_id,save_mode):
    
    symbols = get_symbols(asset_class)
    if not symbols:
        print(f"----No stocks found-----")
        exit()
    
    for symbol in symbols:
        
        print(f"----Starting run for {symbol}-----")
        try:
            process_symbol(symbol,strategy_id,asset_class,save_mode)
            print(f"----Completed run for {symbol}-----")
        except Exception as e:
            print(f"!!!!!!Error completing run for {symbol}!!!!!!!!!")
            continue


if __name__ == "__main__":
    
    asset_class = 'crypto'
    strategy_id = 7
    save_mode = 0
    
    run_backtest(asset_class,strategy_id,save_mode)
    
    
    