from src.core.corestrategy import CoreStrategy
import backtrader as bt

class SimpleMovingAverageStrategy(CoreStrategy):
    params = (
        ('ma_period', 20),
    )

    def __init__(self):
        super().__init__()
        self.sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.ma_period)

    def buy_condition(self):
        return self.dataclose[0] > self.sma[0]

    def sell_condition(self):
        return self.dataclose[0] < self.sma[0]