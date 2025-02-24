from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import backtrader as bt
import src.core.run_test as backtest
from strategy import BaseStrategy
import pandas as pd
import json

def get_data_query(timeframe, symbol):
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
  return query
    
def run_test(symbol,timeframe=1, opt_mode=1):      

      cerebro = bt.Cerebro()  

      # set strategy
      if opt_mode == 1:
            
            cerebro.optstrategy(BaseStrategy,
              max_loss_p = range(1,4,1),
              risk_reward = range(1,8,1)
            )
          
      else:
            cerebro.addstrategy(BaseStrategy)      
      

      # get data query
      query = get_data_query(timeframe,symbol)
                 
      # run backtest
      results = backtest.run(symbol,cerebro,query, timeframe,opt_mode)
      return results
 
if __name__ == "__main__":
    
    symbol = 'IBM'
    df_1_h = run_test(symbol,'1h')
    df_4_h = run_test(symbol,'4h')
    df_1d = run_test(symbol,'1d')
       
    
    df_final = pd.concat([df_1_h,df_4_h,df_1d])
    print(df_final)
    
    