import backtrader as bt


class BaseStrategy(bt.Strategy):
  
    
    def __init__(self):
        
        super().__init__()
        self.order = None
        self.trades = []
        
        
    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.data.datetime[0]
        if isinstance(dt, float):
            dt = bt.num2date(dt)
        print('%s, %s' % (dt.isoformat(), txt))
    
    def notify_trade(self, trade):
      pass
        # if trade.isclosed:
        #     # Gather trade information upon closing
        #     trade_info = {
        #         'entry_time': trade.open_datetime,  # Use strftime for readable format
        #         'exit_time': trade.close_datetime,  # Use strftime for readable format
        #         'entry_price': trade.price,  # Entry price of the trade
        #         'exit_price': trade.close.price,  # Correctly reference the exit (close) price
        #         'quantity': trade.size,  # Quantity of the trade
        #         'profit_loss': trade.pnl  # Profit or loss from the trade
        #     }
        #     self.trades.append(trade_info)
            
            
    
    def stop(self):
        # # Print all trades when the strategy stops
        # print("\nList of all trades:")
        # for trade in self.trades:
        #     print(trade)
        pass
    
    def get_long_entry(self):
            
      raise NotImplementedError("Subclasses should implement this!")
    
    def get_long_exit(self):
      
      raise NotImplementedError("Subclasses should implement this!")
    
    def get_short_entry(self):
      raise NotImplementedError("Subclasses should implement this!")
        
    
    def get_short_exit(self):
      raise NotImplementedError("Subclasses should implement this!")
      

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
        self.open = self.data.open[0]
        self.close_price = self.data.close[0]
        
        print('Position is {}'.format(self.position))
        print('Trade executed at bar {}'.format(self.bar_executed))

      self.order = None

    def next(self):
        
        if self.order:
          return
        try:
          if not self.position:
            if self.get_long_entry():
                self.order = self.buy(size = self.params.size)
            
            elif self.get_short_entry():
                self.order = self.sell(size = self.params.size)
          else:
            if self.position.size > 0:
                if self.get_long_exit():
                  self.close()
                  
            elif self.position.size < 0:
                if self.get_short_exit():
                  self.close()
        
        except Exception as err:
          
          print(f"Unexpected {err=}, {type(err)=}")
 

    
    