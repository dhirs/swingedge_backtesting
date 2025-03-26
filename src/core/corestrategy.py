import backtrader as bt
from tabulate import tabulate
from datetime import datetime

class CoreStrategy(bt.Strategy):
    def __init__(self,child_params):
        self.order = None
        self.trades = []
        self.child_params = child_params
        self.dataclose = self.datas[0].close

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}')
        
    def print_trades(self):
        headers = ['Entry', 'Exit','Qty', 'Price', 'PnL', 'Duration(bars)']
        print("\nTrades:")
        print(tabulate(self.trades, headers=headers, tablefmt='grid'))
        


    
    def print_transactions(self):
        transactions = self.analyzers.transactions.get_analysis()
        table_data = []
        for timestamp, transactions_list in transactions.items():
            for index, transaction in enumerate(transactions_list):
                row = [timestamp, index] + transaction
                table_data.append(row)
        

        # Define the headers for the table
        headers = ['Date/Time', 'Size', 'Price', 'Value', 'Commission', 'PnL']

        # Print the tabulated transactions
        print("\nTransactions:")
        print(tabulate(table_data, headers=headers, tablefmt='grid'))
    
    def stop(self):
        # self.print_transactions()  
        self.print_trades()      
    
    
    def set_execution_params(self,order):
        self.bar_executed = len(self)
        self.execution_price = order.executed.price
        self.low = self.data.low[0]
        self.high = self.data.high[0]
        self.open = self.data.open[0]
        self.close_price = self.data.close[0]

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')
            else:
                self.log(f'SELL EXECUTED, Price: {order.executed.price:.2f}, Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')

            self.set_execution_params(order)
            
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None
        
        
        
    def notify_trade(self, trade):
        if trade.isclosed:
            if trade.isclosed:
            
                trade_info = [
                    bt.num2date(trade.dtopen).strftime('%Y-%m-%d %H:%M:%S'),  # Use strftime for readable format
                    bt.num2date(trade.dtclose).strftime('%Y-%m-%d %H:%M:%S'),  # Use strftime for readable format
                    trade.size,  # Quantity of the trade
                    trade.price,  # Entry price of the trade
                   
                    trade.pnl,  # Profit or loss from the trade
                    trade.barlen
                ]
                self.trades.append(trade_info)
    
    
    
    def next(self):
        if self.order:
            return

        if not self.position:
            if  self.get_long_entry():
                self.log(f'LONG CREATE, {self.dataclose[0]:.2f}')
                self.order = self.buy(size=self.child_params.size)
            elif self.get_short_entry():
                self.log(f'SHORT CREATE, {self.dataclose[0]:.2f}')
                self.order = self.sell(size=self.child_params.size)
        else:
            if self.position.size > 0:
                if self.get_long_exit():
                    self.log(f'LONG EXIT, {self.dataclose[0]:.2f}')
                    self.close()
                  
            elif self.position.size < 0:
                if self.get_short_exit():
                    self.log(f'SHORT EXIT, {self.dataclose[0]:.2f}')
                    self.close()

    def get_long_entry(self):
        # This method should be overridden in child classes
        raise NotImplementedError("long entry condition method must be implemented in child class")

    def get_short_entry(self):
        # This method should be overridden in child classes
        raise NotImplementedError("short entry condition must be implemented in child class")
    
    def get_long_exit(self):
        # This method should be overridden in child classes
        raise NotImplementedError("long exit condition method must be implemented in child class")
    
    def get_short_exit(self):
        # This method should be overridden in child classes
        raise NotImplementedError("short exit condition method must be implemented in child class")