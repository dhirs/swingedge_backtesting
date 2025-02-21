import backtrader as bt
import src.core.run_test as test
import src.core.pandas_data_feed as pdf
import long_entry,long_exit,short_entry,short_exit

class BaseStrategy(bt.Strategy):

       
    def __init__(self):
        self.counter = 0
        self.order = None
        self.macd = bt.indicators.MACD(self.data.close)
        # self.signal = bt.indicators.MACDSignal(self.macd)
        self.strategy_id = 1
        
    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.data.datetime[0]
        if isinstance(dt, float):
            dt = bt.num2date(dt)
        print('%s, %s' % (dt.isoformat(), txt))
        
    def get_long_entry(self):
      if self.macd.macd[0] > self.macd.signal[0]:
        return True
    
    def get_long_exit(self):
      stop_price = self.execution_price*(0.98)
      if self.data.close[0] < stop_price:
        return True
      
      target_price = self.execution_price* 1.04
      if self.data.close[0] >= target_price:
        return True
    
    def get_short_entry(self):
      if self.macd.macd[0] < self.macd.signal[0]:
        return True
    
    def get_short_exit(self):
      stop_price = self.execution_price * (1.02)
      if self.data.close[0] > stop_price:
        return True
      
      target_price = self.execution_price* 0.96
      if self.data.close[0] <= target_price:
        return True
      

    def notify_order(self,order):

      if order.status in [order.Completed]:
        if order.isbuy():
          self.log('Buy executed at:{}'.format(order.executed.price))

        elif order.issell():
          self.log('Sell executed at:{}'.format(order.executed.price))

        self.bar_executed = len(self)
        self.execution_price = order.executed.price
        # print('Position is {}'.format(self.position))
        # print('Trade executed at bar {}'.format(self.bar_executed))

      self.order = None

    def next(self):
        # print(self.order)
        # print(self.position)
        # print(len(self))
        if self.order:
          return
        
        if not self.position:
          if self.get_long_entry():
              self.order = self.buy()
          
          elif self.get_short_entry():
              self.order = self.sell()
        else:
          if self.position.size > 0:
              if self.get_long_exit():
                self.close()
                
          elif self.position.size < 0:
              if self.get_short_exit():
                self.close()
                

# execute strategy
strategy_id = 1
query = "select * from one_h_mh where symbol = 'IBM'"
test.run('IBM',query,BaseStrategy)

