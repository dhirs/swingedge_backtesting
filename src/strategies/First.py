from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import backtrader as bt
import backtrader.analyzers as bta
import psycopg2 as db
import pandas as pd
import pandas.io.sql as sqlio
from matplotlib import pyplot as plt

db_username = 'tsdbadmin'
db_password = 'letin1234$Agf'
db_url = 'jdbc:postgresql://w25uxmcny6.m8iecjpjs8.tsdb.cloud.timescale.com:30127/tsdb'
db_host = 'w25uxmcny6.m8iecjpjs8.tsdb.cloud.timescale.com'
db_table = 'us_etfs_stocks'
db_ = 'tsdb'
db_port = 30127
conn = db.connect(
database=db_,
user=db_username,
password=db_password,
host=db_host,
port=db_port)


query = "select * from one_h_mh where symbol = 'IBM'"
df = sqlio.read_sql_query(query, conn)


class PandasData(bt.feeds.PandasData):
    params = (
        ('datetime', 'bucket'),
        ('open', -1),
        ('high', -1),
        ('low', -1),
        ('close', -1),
        ('volume', -1),
    )
data_feed = PandasData(dataname=df)


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


cerebro = bt.Cerebro()  # create a "Cerebro" engine instance
cerebro.addstrategy(FirstStrategy)
cerebro.adddata(data_feed)

cerebro.addanalyzer(bta.SharpeRatio, _name='mysharpe')
cerebro.addanalyzer(bta.DrawDown, _name='drawdown')
cerebro.addanalyzer(bta.TradeAnalyzer, _name='trades')

results = cerebro.run()

sharpe = results[0].analyzers.mysharpe.get_analysis()
drawdown = results[0].analyzers.drawdown.get_analysis()
trades = results[0].analyzers.trades.get_analysis()

# print(f'Sharpe Ratio: {sharpe["sharperatio"]}')
# print(f'Max Drawdown: {drawdown["max"]["drawdown"]}')
print(f'Total Trades: {trades.total.total}')
print(f'Open Trades: {trades.total.open}')
print(f'Closed Trades: {trades.total.closed}')
print(f'Total wins: {trades.won.total}')
print(f'Total lost: {trades.lost.total}')
print('**********Win ratio************')
win_ratio  = trades.won.total/(trades.won.total+trades.lost.total)
print(win_ratio)
print('*******************************')
print('**********Profit/trade************')
net_profit_per_trade = (trades.won.pnl.total + trades.lost.pnl.total)/trades.total.closed
print(net_profit_per_trade )
print('*******************************')
print(f'Total profit: {trades.won.pnl.total}')
print(f'Total loss: {trades.lost.pnl.total}')
print('************Longs***********')
print(f'Total long trades {trades.long.total}')
print(f'Total long wins {trades.long.won}')
print(f'Total long losses {trades.long.lost}')
print(f'Total long revenue {trades.long.pnl.total}')
print('************Shorts***********')
print(f'Total short trades {trades.short.total}')
print(f'Total short wins {trades.short.won}')
print(f'Total short losses {trades.short.lost}')
print(f'Total short revenue {trades.short.pnl.total}')