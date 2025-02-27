from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import backtrader as bt
import src.core.run_test as backtest
from strategy import BaseStrategy
import pandas as pd
import json
from src.core.db import Database as db
import warnings
warnings.filterwarnings('ignore')
import traceback 

def eval_params(opt_mode, strategy_class, params):
      if opt_mode == 1:
            
            list = []
            for key, value in params.items():
                  list.append(f"{key} = {value}")
                  
            param_str = strategy_class + ","+",".join(list)
            final_str = f"cerebro.optstrategy({param_str})"
      else:
            param_str = strategy_class
            final_str = f"cerebro.addstrategy({param_str})"
            
      return final_str


def run_loop(symbol,timeframe='1h', opt_mode=1,run_loop_done=False):      

      cerebro = bt.Cerebro()  
      params = {'max_loss_p':'range(1,4,1)', 
                  'risk_reward' :'range(1,8,1)'}
      strategy_class = 'BaseStrategy'
      
      cerebro_strategy_params = eval_params(opt_mode, strategy_class,params)
      
      # set strategy
      # if opt_mode == 1:
            
      #       cerebro.optstrategy(BaseStrategy,
      #         max_loss_p = range(1,4,1), 
      #         risk_reward = range(1,8,1)
      #       )
          
      # else:
      #       cerebro.addstrategy(BaseStrategy) 
      
      eval(cerebro_strategy_params)     
      
      backtest.getResults(symbol,cerebro,timeframe,opt_mode,run_loop_done)
      

def run(symbol):
 
  periods = ['1h','4h','1d']
  
  run_loop_done = False
  count = 0
  
  for timeframe in periods:
    count += 1
    if count == len(periods):
       run_loop_done = True
       count = 0 
    run_loop(symbol=symbol,timeframe=timeframe,run_loop_done=run_loop_done)
      

if __name__ == "__main__":
    
      # symbols = ['IBM','NVIDIA','TSLA','META','AMZN','MSFT','NFLX','APPL','GOOGL']
      symbols = ['IBM']
  
      for symbol in symbols:
  
            run(symbol)
     
    
    
    