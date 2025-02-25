import backtrader.analyzers as bta
import json
import pandas as pd
import numpy as np
import src.core.pandas_data_feed as pdf
from src.core.db import Database as db
import time
import base64
from datetime import datetime, timezone
pd.set_option('display.max_columns',None)


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
    cerebro.addanalyzer(bta.Transactions, _name='transactions')

def collect_results_opt(results,timeframe):
    # par_list = [
    #         [
    #         x[0].params.max_loss_p, 
    #         x[0].params.risk_reward,
    #         x[0].analyzers.returns.get_analysis()['rnorm100'], 
    #         x[0].analyzers.drawdown.get_analysis()['max']['drawdown'],
    #         x[0].analyzers.sharpe.get_analysis()['sharperatio'],
    #         x[0].analyzers.trades.get_analysis()['pnl']['net']['total'],
    #         x[0].analyzers.trades.get_analysis()['won']['total'],
    #         x[0].analyzers.trades.get_analysis()['won']['pnl']['total'],
    #         x[0].analyzers.trades.get_analysis()['lost']['total'],
    #         x[0].analyzers.trades.get_analysis()['lost']['pnl']['total'],
    #         x[0].analyzers.trades.get_analysis()['long']['won'],
    #         x[0].analyzers.trades.get_analysis()['long']['lost'],
    #         x[0].analyzers.trades.get_analysis()['short']['won'],
    #         x[0].analyzers.trades.get_analysis()['short']['lost'],
    #         x[0].analyzers.trades.get_analysis()['len'],
    #         x[0].analyzers.transactions.get_analysis(),
    #         timeframe
    #         ] for x in results]
    
    par_list = [
            [
            x[0].params.max_loss_p, 
            x[0].params.risk_reward,
            x[0].analyzers.returns.get_analysis(), 
            x[0].analyzers.drawdown.get_analysis(),
            x[0].analyzers.sharpe.get_analysis(),
            x[0].analyzers.trades.get_analysis(),
            x[0].analyzers.trades.get_analysis()['pnl']['net']['total'], ##net pnl
            x[0].analyzers.trades.get_analysis()['won']['pnl']['total'],  ##total wins
            x[0].analyzers.trades.get_analysis()['lost']['pnl']['total'],  ##total_losses
            x[0].analyzers.transactions.get_analysis(),
            timeframe
            ] for x in results]
    
    # print(par_list)
    
    df = pd.DataFrame(par_list, columns = ['max_loss_p',                                            
                                           'risk_reward', 
                                           'returns','drawdown','sharpe','trades',
                                           'net_pnl',
                                           'total_wins',
                                           'total_losses',
                                           'transactions','timeframe'                                      
                                           ])
    
    # print(df.head())
    tail = 5
    
    # df['win_ratio'] = df['total_wins'] / (df['total_wins'] + df['total_losses'])
    df1 = df.sort_values(by='net_pnl').tail(tail)
    last_row = df1.iloc[-1]
    pnl = last_row['net_pnl']
    wins = last_row['total_wins']
    losses = last_row['total_losses']
    
    opt_param = {'max_loss_p': float(last_row['max_loss_p']),
                 'risk_reward': float(last_row['risk_reward'])}
    opt_param_json = json.dumps(opt_param)
    timeframe = last_row['timeframe']
    
    return  df,pnl,wins,losses,opt_param_json,timeframe
    
    
      
       
def collect_results(results,timeframe):
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
                "timeframe" : [timeframe]
                }
        
    df = pd.DataFrame.from_dict(dict)
    
    # js = json.dumps(df)
    # print(df.to_json())
    return df


def generate_payload(symbol,metrics,opt_mode):
    if opt_mode==1:
        strategy = 1
        run_time = datetime.now(timezone.utc)
        value_json = metrics[0].to_json(orient="records", indent=4)
        value_base64 = base64.b64encode(value_json.encode()).decode()
        
        return [symbol,strategy,run_time,value_base64,metrics[1],metrics[2],metrics[3],metrics[4],metrics[5]]
        # print(value_json)
        # with open('payload.json',"w",encoding='utf-8') as json_file:
        #         json_file.write(value_json)
        
       
    else:
        strategy = 1
        run_time = time.time()
        metrics_json = metrics.to_json(orient="records") 
        # keys = ["symbol", "strategy", "run_time", "metrics"]
        # values = [symbol, strategy, run_time, metrics]
        # payload = dict(zip(keys, values))
        # for key,value in payload.items():
        #     print(f"key: {key} | value: {value}")
        # df = pd.DataFrame.from_dict(payload)
        # print(df)
        # return df
        
        payload = {
            "symbol": symbol,
            "strategy": strategy,
            "run_time": run_time,
            "metrics": metrics_json
        }


        metrics_list = json.loads(payload["metrics"]) 
        df_expanded = pd.DataFrame(metrics_list)
        df_expanded["symbol"] = payload["symbol"]
        df_expanded["strategy"] = payload["strategy"]
        df_expanded["run_time"] = payload["run_time"]

        df_compact = pd.DataFrame([payload])  

        for key,value in payload.items():
            print(f"key: {key} | value: {value}")





def run(symbol,cerebro, query, timeframe, opt_mode):
    print(__name__,"opt mode: ",opt_mode)
    # add data to cerebro
    data = get_data(query)
    cerebro.adddata(data)
    
    # add analysers
    add_analyzers(cerebro)

    # run backtest
    results = cerebro.run()
    
    # collect results
    if opt_mode == 1:   
        df,pnl,wins,losses,opt_params,timeframe = collect_results_opt(results,timeframe)

        
    else:
        metrics = collect_results(results,timeframe)
    
   
    # generate payload
    info = generate_payload(symbol=symbol, metrics=[df,pnl,wins,losses,opt_params,timeframe], opt_mode=opt_mode)
    # print(info)
    
    
    # update metrics in db
    database = db()
    database.update_results(info)
    
    
    return info
    
