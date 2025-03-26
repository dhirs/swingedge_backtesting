from src.core.corestrategy import CoreStrategy
import backtrader as bt

class SMAStrategy(CoreStrategy):
    params = (
        ('ma_period', 20),
        ('size',0.005),
         ('rr',5)
    )

    def __init__(self):
        super().__init__(self.params)
        self.sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.ma_period)

    def get_long_entry(self):
        return self.dataclose[0] > self.sma[0]
    
    def get_long_exit(self):
        # stop loss
        if self.dataclose[0] < self.low:
            return True
        # take profit
        if self.dataclose[0] > (1+self.params.rr/100)*self.execution_price:
            return True
    
    def get_short_entry(self):
        return self.dataclose[0] < self.sma[0]
    
    def get_short_exit(self):
        if self.dataclose[0] > self.high:
            return True
        # take profit
        if self.dataclose[0] < (1-self.params.rr/100)*self.execution_price:
            return True