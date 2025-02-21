from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import backtrader as bt
import backtrader.analyzers as bta
import src.core.analyzer as analyzer
import src.core.pandas_data_feed as pdf

def run(symbol, query,strategy):
    
    # create a "Cerebro" engine instance
    cerebro = bt.Cerebro()  
    
    # add strategy
    # cerebro.addstrategy(strategy)
    
    cerebro.optstrategy(
        strategy,
        fast_period=range(1,12,4),
        slow_period=range(1,26,8),
        signal_period=range(1,9,5)
        )
    

    data_feed = pdf.get_data_feed(query)
    cerebro.adddata(data_feed)

    # add analyzers
    cerebro.addanalyzer(bta.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bta.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bta.TradeAnalyzer, _name='trades')

    # run strategy
    results = cerebro.run()

    # collect results
    analyzer.collect_strategy_stats(symbol, results)