import backtrader.analyzers as bta
import json
import pandas as pd
import src.core.pandas_data_feed as pdf
from src.core.db import Database as db


# get data
def get_data(query):
    
    # add data feed      
    data_feed = pdf.get_data_feed(query)
    return data_feed

# add analyzers
def add_analyzers(cerebro):
    cerebro.addanalyzer(bta.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bta.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bta.TradeAnalyzer, _name='trades')
    cerebro.addanalyzer(bta.Returns, _name='returns')

def collect_results_opt(results):
    par_list = [
            [
            x[0].params.max_loss_p, 
            x[0].params.risk_reward,
            x[0].analyzers.returns.get_analysis()['rnorm100'], 
            x[0].analyzers.drawdown.get_analysis()['max']['drawdown'],
            x[0].analyzers.sharpe.get_analysis()['sharperatio'],
            x[0].analyzers.trades.get_analysis()['pnl']['net']['total'],
            x[0].analyzers.trades.get_analysis()['won']['total'],
            x[0].analyzers.trades.get_analysis()['won']['pnl']['total'],
            x[0].analyzers.trades.get_analysis()['lost']['total'],
            x[0].analyzers.trades.get_analysis()['lost']['pnl']['total'],
            x[0].analyzers.trades.get_analysis()['long']['won'],
            x[0].analyzers.trades.get_analysis()['long']['lost'],
            x[0].analyzers.trades.get_analysis()['short']['won'],
            x[0].analyzers.trades.get_analysis()['short']['lost'],
            ] for x in results]
    df = pd.DataFrame(par_list, columns = ['max_loss_p',                                            
                                           'risk_reward', 
                                           'return','drawdown','sharpe','net_pnl',
                                           'total_wins','gross_profit',
                                           'total_losses','gross_loss',
                                           'long_won','long_lost',
                                           'short_won','short_lost',
                                           
                                           ])
    # df.loc[df['rt'].idxmax()]
    # df = pd.DataFrame(par_list, columns =['total'])
    print(df)
    return df
    # print(json.dumps(df.iloc[0].values.flatten().tolist()))
      
       
def collect_results(results):
    sharpe = results[0].analyzers.sharpe.get_analysis()
    drawdown = results[0].analyzers.drawdown.get_analysis()
    trades = results[0].analyzers.trades.get_analysis()
    rets = results[0].analyzers.returns.get_analysis()
    dict = {"sharpe":[sharpe["sharperatio"]],
                "drawdown" : [drawdown["max"]["drawdown"]],
                "return" : [rets['rnorm100']],
                "won" : [trades["won"]["total"]],
                "lost": [trades["lost"]["total"]],
                "win_ratio" : [trades.won.total/(trades.won.total+trades.lost.total)],
                "total_profit": [trades.won.pnl.total],
                "total_loss": [trades.lost.pnl.total],
                "net_profit": [trades.pnl.net.total],
                "long_trades" : [trades.long.total],
                "long_wins" : [trades.long.won],
                "long_losses" : [trades.long.lost],
                "long_net_revenue" : [trades.long.pnl.total],
                "short_trades" : [trades.short.total],
                "short_wins" : [trades.short.won],
                "short_losses" : [trades.short.lost],
                "short_net_revenue" : [trades.short.pnl.total],
                }
        
    df = pd.DataFrame.from_dict(dict)
    print(df)
    # js = json.dumps(df)
    # print(df.to_json())
    return df

def generate_payload(symbol,metrics,opt_mode):
    pass


def run(symbol,cerebro, query, opt_mode=None):
    
    # add data to cerebro
    data = get_data(query)
    cerebro.adddata(data)
    
    # add analysers
    add_analyzers(cerebro)

    # run backtest
    results = cerebro.run()
    
    # collect results
    if not opt_mode:
        metrics = collect_results(results)
    else:
        metrics = collect_results_opt(results)
    
    # generate payload
    payload = generate_payload(symbol, metrics, opt_mode)
    
    # update metrics in db
    database = db()
    db.update_results(symbol,payload,opt_mode)
    
