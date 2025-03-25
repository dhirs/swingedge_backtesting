import backtrader as bt


class CoreStrategy(bt.Strategy):
    def __init__(self):
        self.order = None
        self.dataclose = self.datas[0].close

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}')

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')
            else:
                self.log(f'SELL EXECUTED, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def next(self):
        if self.order:
            return

        if not self.position:
            if self.buy_condition():
                self.log(f'BUY CREATE, {self.dataclose[0]:.2f}')
                self.order = self.buy(size=0.005)
        else:
            if self.sell_condition():
                self.log(f'SELL CREATE, {self.dataclose[0]:.2f}')
                self.order = self.sell(size=0.005)

    def buy_condition(self):
        # This method should be overridden in child classes
        raise NotImplementedError("buy_condition method must be implemented in child class")

    def sell_condition(self):
        # This method should be overridden in child classes
        raise NotImplementedError("sell_condition method must be implemented in child class")