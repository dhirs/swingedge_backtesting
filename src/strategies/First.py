import backtrader as bt
import src.core.base_strategy as base_strategy

class FirstStrategy(bt.Strategy):

       
    def log(self,txt, dt=None):
        dt = dt or self.data.datetime[0]
        print(txt)

    def __init__(self):
        self.counter = 0
        self.order = None

    def notify_order(self,order):

      if order.status in [order.Completed]:
        if order.isbuy():
          pass
          # self.log('Buy executed at:{}'.format(order.executed.price))

        elif order.issell():
          pass
          #  self.log('Sell executed at:{}'.format(order.executed.price))

        self.bar_executed = len(self)
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
          if (self.data.close[0] > self.data.close[-1] and self.data.close[-1] > self.data.close[-2]):
              self.order = self.buy()
        else:
          if len(self) ==  (self.bar_executed + 4):
              self.order = self.sell()


# get query to be used for strategy
query = "select * from one_h_mh where symbol='IBM'"

# set symbol
symbol = 'IBM'

# execute strategy
base_strategy.run(symbol,query,FirstStrategy)

