import backtrader as bt
import src.core.run_test as backtest

class BaseStrategy(bt.Strategy):
  
    params = (
       
        ('max_loss_p' , 1),
        ('risk_reward', 4)
          
    )
 
    def __init__(self):
        
        self.counter = 0
        self.order = None
       
        self.macd = bt.indicators.MACD(self.data.close)
        self.mcross = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)
        
    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.data.datetime[0]
        if isinstance(dt, float):
            dt = bt.num2date(dt)
        # print('%s, %s' % (dt.isoformat(), txt))
        
    def get_long_entry(self):
            
      if self.mcross[0] > 0.0:                                
      # if self.macd.macd[0] > self.macd.signal[0]:
        if self.macd.macd[0] < 0 and self.macd.signal[0] < 0:
          return True
    
    def get_long_exit(self):
      # stop_price = self.execution_price*(1-self.params.max_loss_p/100)
      # if self.data.close[0] < stop_price:
      if self.data.close[0] < self.low:
        return True
      
      target_price = self.execution_price*(1+ self.params.risk_reward/100)
      if self.data.close[0] >= target_price:
        return True
    
    def get_short_entry(self):
      if self.mcross[0] < 0.0:  
        if self.macd.macd[0] > 0 and self.macd.signal[0] > 0:
          return True
        
    
    def get_short_exit(self):
      # stop_price = self.execution_price *(1+self.params.max_loss_p/100)
      # if self.data.close[0] > stop_price:
      if self.data.close[0] > self.high:
        return True
      
      target_price = self.execution_price*(1-self.params.risk_reward/100)
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
        self.low = self.data.low[0]
        self.high = self.data.high[0]
        # print('Position is {}'.format(self.position))
        # print('Trade executed at bar {}'.format(self.bar_executed))

      self.order = None

    def next(self):
        # print(self.order)
        # print(self.position)
        # print(len(self))
        if self.order:
          return
        try:
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
        except Exception as err:
          pass
          # print(f"Unexpected {err=}, {type(err)=}")
 
if __name__ == "__main__":
    
      symbols = ['IBM','NVIDIA','TSLA','META','AMZN','ADBE', 'INTC', 'MSFT','NFLX','APPL','GOOGL']
      
      # symbols = ['TSLA']           
      
      for symbol in symbols:
        strategy_obj = bt.Cerebro() 
        strategy_obj.optstrategy(BaseStrategy,
                          max_loss_p = range(1,4,1),
                          risk_reward = range(1,8,1)
                          )
  
        backtest.run(symbol,strategy_obj)