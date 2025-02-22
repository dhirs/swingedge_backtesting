from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import backtrader as bt
import src.core.run_test as backtest
from strategy import BaseStrategy

def get_data_query():
  query = "select * from one_h_mh where symbol = 'IBM'"
  return query
    
def run_test(symbol,opt_mode=None):      

      cerebro = bt.Cerebro()  

      # set strategy
      if not opt_mode:
          cerebro.addstrategy(BaseStrategy)
      else:
          cerebro.optstrategy(
              BaseStrategy,
              max_loss_p = range(1,4,1),
              risk_reward = range(1,8,1)        
      )

      # get data query
      query = get_data_query()
                 
      # run backtest
      backtest.run(symbol,cerebro,query, opt_mode)
 
if __name__ == "__main__":
    
    run_test('IBM',1)