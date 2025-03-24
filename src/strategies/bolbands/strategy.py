import backtrader as bt
from backtrader.indicators import BollingerBands

class BaseStrategy(bt.Strategy):
  
    
       
    params = (
  ('period', 20),
  ('devfactor', 2),
  ('size', 0.001),
  ('risk_reward', 2),
  ('size',0.005)
    )
          
   
 
    def __init__(self):
        
        self.bb = bt.indicators.BollingerBands(self.data.close, period=self.params.period, devfactor=self.params.devfactor)
        self.order = None
        self.trades = []
        
        
    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.data.datetime[0]
        if isinstance(dt, float):
            dt = bt.num2date(dt)
            print('%s, %s' % (dt.isoformat(), txt))
        
    def get_long_entry(self):
           
      if self.data.close[0]  > self.bb.lines.mid[0]:                            
        if self.data.open[0] < self.bb.lines.mid[0]:
          return True
    
    def get_long_exit(self):
      
      if self.data.close[0] < self.stop_price:
      
        return True
      
      # target_price = self.execution_price*(1+ self.params.risk_reward/100)
      if self.data.close[0] >= self.target_price:
        return True
    
    def get_short_entry(self):
      
      if self.data.close[0]  < self.bb.lines.mid[0]  :  
        if self.data.open[0] > self.bb.lines.mid[0]:
         
          return True
        
    
    def get_short_exit(self):
      
      if self.data.close[0] > self.stop_price:
      
        return True
      
      # target_price = self.execution_price*(1-self.params.risk_reward/100)
      if self.data.close[0] <= self.target_price:
        return True
      
    def print_order(self,order):
      # pass
        print("Order ID:", order.ref)
        print("Status:", order.getstatusname())
        
        print("Size:", order.size)
        print("Price:", order.price)
        print("Created at:", order.created)
        # print("Executed at:", order.executed.dt if order.executed else "Not executed")
        if order.executed:
            print("Executed size:", order.executed.size)
            print("Executed price:", order.executed.price)
            print("Commission:", order.executed.comm)
        
        print("Pending:", order.isbuy() or order.issell())  # Check if the order is pending
        # print("Link to the original order:", order.link)
    
    def notify_order(self,order):
      
      # self.print_order(order)
      
      if order.status in [order.Submitted, order.Accepted]:
            return
          
      if order.status == order.Completed:
        # print(order.status)
        
          
        # if order.isbuy():
        #   # self.log('Buy executed at:{}'.format(order.executed.price))

        # elif order.issell():
          # self.log('Sell executed at:{}'.format(order.executed.price))

        self.bar_executed = len(self)
        self.execution_price = order.executed.price
        self.low = self.data.low[0]
        self.high = self.data.high[0]
        
        if order.isbuy():
          self.risk  = self.data.close[0]-self.data.low[0]
          self.stop_price = self.data.low[0]
          self.target_price = self.execution_price + self.risk*self.params.risk_reward
          # print(self.bar_executed)
          # print(self.target_price)
        
        if order.issell():
          self.risk  = self.data.high[0]-self.data.close[0]
          self.stop_price = self.data.high[0]
          self.target_price = self.execution_price - self.risk*self.params.risk_reward
          # print(self.bar_executed)
          # print(self.target_price)
        

      self.order = None

    def next(self):
        
        # current_date = self.data.datetime.date(0)  # This gets the date without time
        # print(f'Current bar date: {current_date}')
        if self.order:
          return
        try:
          if not self.position:
            if self.get_long_entry():
                self.order = self.buy(price=self.data.close[0],size=self.params.size)
                # self.log('Long trade executed')
            elif self.get_short_entry():
                self.order = self.sell(price=self.data.close[0],size=self.params.size)
                # self.log('Short trade executed')
          else:
            if self.position.size > 0:
                if self.get_long_exit():
                    # self.log('Exiting long trade')
                    self.close()
            elif self.position.size < 0:
                if self.get_short_exit():
                    # self.log('Exiting short trade')
                    self.close()
        except Exception as err:
          
          print(f"Unexpected {err=}, {type(err)=}")
 

    
    