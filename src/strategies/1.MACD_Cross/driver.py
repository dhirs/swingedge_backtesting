from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import backtrader as bt
import src.core.run_test as backtest
from strategy import BaseStrategy
import pandas as pd
import json
from src.core.db import Database as db

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
    
def run_loop(symbol,timeframe=1, opt_mode=1,run_loop_done=False):      

      cerebro = bt.Cerebro()  

      # set strategy
      if opt_mode == 1:
            
            cerebro.optstrategy(BaseStrategy,
              max_loss_p = range(1,4,1),  ##loss i am willing to accept
              risk_reward = range(1,8,1)
            )
          
      else:
            cerebro.addstrategy(BaseStrategy)      
      

      # get data query
      query = get_data_query(timeframe,symbol)
                 
      # run backtest
      print("opt mode: ",opt_mode)
      results = backtest.getResults(symbol,cerebro,query, timeframe,opt_mode,run_loop_done)
      return results

def run(symbol):
  df_1h = run_loop(symbol,'1h')
  df_4h = run_loop(symbol,'4h')
  df_1d = run_loop(symbol,'1d')
  
  df_dict = {'1h':df_1h,
             '4h':df_4h,
             '1d':df_1d}
  
  run_loop_done = False
  count = 0
  # print(df_1_h)
  for timeframe,value in df_dict.items():
    count += 1
    if count == len(df_dict):
       run_loop_done = True  
    run_loop(symbol=symbol,timeframe=timeframe,run_loop_done=run_loop_done)
  
  
  # final_info = pd.concact()
  # # update metrics in db
  # database = db()
  # for info in dfs:
  #     database.update_results(info)
      

if __name__ == "__main__":
    
  symbol = 'IBM'
  run(symbol)
    
    
    