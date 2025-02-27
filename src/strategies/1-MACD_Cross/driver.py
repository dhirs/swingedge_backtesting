import backtrader as bt
from strategy import BaseStrategy
import src.core.run_test as backtest
import src.core.pandas_data_feed as pdf



def get_data(timeframe, symbol):
    if timeframe == '1h':
        table_name = 'one_h_mh'
    
    elif timeframe == '4h':
        table_name = 'four_h_mh'
        
    elif timeframe == '1d':
        table_name = 'daily_mh'
   
        
    elif timeframe == '1w':
        table_name = 'weekly_mh'
        
    elif timeframe == '1m':
        table_name = 'monthly_mh'
    
    
    query = f"select * from {table_name} where symbol = '{symbol}'"
      
    data_feed = pdf.get_data_feed(query)
    return data_feed
# symbols = ['IBM','NVIDIA','TSLA','META','AMZN','ADBE', 'INTC', 'MSFT','NFLX','APPL','GOOGL']

def run(symbol,opt_mode=1):
 
  periods = ['1h','4h','1d']
  
  run_loop_done = False
  count = 0
  
  for timeframe in periods:
    count += 1
    
    
    if count == len(periods):
       run_loop_done = True
       count = 0 
    
    backtest_strategy = bt.Cerebro() 
    backtest_strategy.optstrategy(BaseStrategy,
                        max_loss_p = range(1,4,1),
                        risk_reward = range(1,8,1)
                        )
     
    # add data to cerebro strategy object
    data = get_data(timeframe,symbol)
    
    if data is None:
        print(f"!!!!!!!!!No data found for {symbol}, in timeframe {timeframe}!!!!!!")
        return
    
    backtest_strategy.adddata(data)
    print(f"-----Found data for {symbol},{timeframe}-----")
   
    backtest.getResults(symbol,backtest_strategy, timeframe,run_loop_done,opt_mode)    

   
symbols = ['IBM']           

for symbol in symbols:
    
    run(symbol)