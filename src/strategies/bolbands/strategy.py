import backtrader as bt
from backtrader.indicators import BollingerBands

class BaseStrategy(bt.Strategy):
  
    params = (
       
        ('max_loss_p' , 1),
        ('risk_reward', 9)
          
    )
    id = None
 
    def __init__(self):
        
        self.counter = 0
        self.order = None
       
        self.bb = BollingerBands(period=20, devfactor=2)
        
        
    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.data.datetime[0]
        if isinstance(dt, float):
            dt = bt.num2date(dt)
            print('%s, %s' % (dt.isoformat(), txt))
        
    def get_long_entry(self):
      print(self.data.close[0])  
      print(self.data.open[0])  
       
      print(self.bb.mid[0])  
      dt = self.data.datetime[0]
      dt = bt.num2date(dt)
      print(dt.isoformat())
      
      if self.data.close[0]  > self.bb.mid[0]:                            
        if self.data.open[0] < self.bb.mid[0]:
          return True
    
    def get_long_exit(self):
      stop_price = self.execution_price*(1-self.params.max_loss_p/100)
      if self.data.close[0] < stop_price:
      # if self.data.close[0] < self.low:
        return True
      
      # target_price = self.execution_price*(1+ self.params.risk_reward/100)
      if self.data.close[0] >= self.target_price:
        return True
    
    def get_short_entry(self):
      print(self.data.close[0])  
      print(self.bb.mid[0])  
      print(self.data.open[0])  
      
      dt = self.data.datetime[0]
      dt = bt.num2date(dt)
      print(dt.isoformat())
      if self.data.close[0]  < self.bb.mid[0]  :  
        if self.data.open[0] > self.bb.mid[0]:
         
          return True
        
    
    def get_short_exit(self):
      stop_price = self.execution_price *(1+self.params.max_loss_p/100)
      if self.data.close[0] > stop_price:
      # if self.data.close[0] > self.high:
        return True
      
      # target_price = self.execution_price*(1-self.params.risk_reward/100)
      if self.data.close[0] <= self.target_price:
        return True
      

    def notify_order(self,order):
      print(order.status)
      if order.status in [order.Completed]:
        if order.isbuy():
          self.log('Buy executed at:{}'.format(order.executed.price))

        elif order.issell():
          self.log('Sell executed at:{}'.format(order.executed.price))

        self.bar_executed = len(self)
        self.execution_price = order.executed.price
        self.low = self.data.low[0]
        self.high = self.data.high[0]
        
        if order.isbuy():
          self.risk  = self.data.close[0]-self.data.low[0]
          self.target_price = self.execution_price + self.risk*self.params.risk_reward
        
        if order.issell():
          self.risk  = self.data.high[0]-self.data.close[0]
          self.target_price = self.execution_price - self.risk*self.params.risk_reward
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
 

    
    