import json
import pandas as pd
# import qgrid
          
def collect_strategy_stats(symbol,results):
      
      # sharpe = results[0].analyzers.sharpe.get_analysis()
      # drawdown = results[0].analyzers.drawdown.get_analysis()
      # trades = results[0].analyzers.trades.get_analysis()
      
      # print(json.dumps(trades, indent=4, default=str))

      # print(f'Sharpe Ratio: {sharpe["sharperatio"]}')
      # print(f'Max Drawdown: {drawdown["max"]["drawdown"]}')
      # print(f'Total Trades: {trades.total.total}')
      # print(f'Open Trades: {trades.total.open}')
      # print(f'Closed Trades: {trades.total.closed}')
      # print(f'Total wins: {trades.won.total}')
      # print(f'Total lost: {trades.lost.total}')
      # print('**********Win ratio************')
      # win_ratio  = trades.won.total/(trades.won.total+trades.lost.total)
      # print(win_ratio)
      # print('*******************************')
      # print('**********Profit/trade************')
      # net_profit_per_trade = (trades.won.pnl.total + trades.lost.pnl.total)/trades.total.closed
      # print(net_profit_per_trade )
      # print('*******************************')
      # print(f'Total profit: {trades.won.pnl.total}')
      # print(f'Total loss: {trades.lost.pnl.total}')
      # print(f'Net profit: {trades.pnl.net.total}')
      # print('************Longs***********')
      # print(f'Total long trades {trades.long.total}')
      # print(f'Total long wins {trades.long.won}')
      # print(f'Total long losses {trades.long.lost}')
      # print(f'Total long revenue {trades.long.pnl.total}')
      # print('************Shorts***********')
      # print(f'Total short trades {trades.short.total}')
      # print(f'Total short wins {trades.short.won}')
      # print(f'Total short losses {trades.short.lost}')
      # print(f'Total short revenue {trades.short.pnl.total}')
      
      # optimized_results = cerebro.run(maxcpus=1)
      par_list = [[x[0].params.fast_period, 
             x[0].params.slow_period,
             x[0].params.signal_period,
             x[0].analyzers.trades.get_analysis(), 
             
            ] for x in results]
      par_df = pd.DataFrame(par_list, columns = ['fast_period', 'slow_period', 'signal_period', 'pnl'])
      print(par_df)

      #   dataFrame = pd.read_json(json.dumps(rets))
        #Printing the data Frame
      #   print(dataFrame)
      #   print('Strat {} Name {}:\n  - analyzer: {}\n'.format(
      #       i, strat.__class__.__name__, rets))
                  