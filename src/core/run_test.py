import backtrader.analyzers as bta
import json
import pandas as pd
import numpy as np
import src.core.pandas_data_feed as pdf
from src.core.db import Database as db
import time
import base64
from datetime import datetime, timezone
import warnings
warnings.filterwarnings('ignore')




pd.set_option('display.max_columns',None)
all_results = {}

def get_data(timeframe, symbol):
    if timeframe == '1h':
        table_name = 'one_h_mh'
    
    elif timeframe == '4h':
        table_name = 'four_h_mh'
        
    elif timeframe == '1d':
        table_name = 'daily_mh'
   
        
    elif timeframe == '1w':
        table_name = 'weekly_mh'
        
    elif timeframe == '1m':
        table_name = 'monthly_mh'
    
    
    query = f"select * from {table_name} where symbol = '{symbol}'"
      
    data_feed = pdf.get_data_feed(query)
    return data_feed

# add analyzers
def add_analyzers(cerebro):
    cerebro.addanalyzer(bta.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bta.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bta.TradeAnalyzer, _name='trades')
    cerebro.addanalyzer(bta.Returns, _name='returns')
    cerebro.addanalyzer(bta.Transactions, _name='transactions')
    return cerebro

def collect_results_opt(results,timeframe):
     
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
    
    resultDf= pd.DataFrame(par_list, columns = ['max_loss_p',                                            
                                           'risk_reward', 
                                           'returns','drawdown','sharpe','trades',
                                           'net_pnl',
                                           'total_wins',
                                           'total_losses',
                                           'transactions','timeframe'                                      
                                           ])
    
    
    
    return  resultDf
    
       
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
    
    return df


def generate_payload(symbol,metrics,opt_mode):
    if opt_mode==1:
        strategy = 1
        run_time = datetime.now(timezone.utc)
        
        df_json = metrics['dataframe'][1].to_json(orient="records", indent=4)
        df_base64 = base64.b64encode(df_json.encode()).decode()
        best_result_json = metrics['dataframe'][0].to_json(orient="records", indent=4)
        best_base64 = base64.b64encode(best_result_json.encode()).decode()
        
        
        metrics['payload_all_base64'] = df_base64
        metrics['payload_best_base64'] = best_base64
        metrics['run_time'] = run_time
        metrics['strategy_id'] = strategy
        metrics['symbol'] = symbol
        return metrics
        
        
       
    else:
        strategy = 1
        run_time = time.time()
        metrics_json = metrics.to_json(orient="records") 
                
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
        

def CompareResults(all_results):
    print(len(all_results))
    
    df_list = [info for timeframe, info in all_results.items()]  
    raw_df = pd.concat(df_list, ignore_index=True)

    ##sort by pnl in descending order and fetch the top record
    final_df = raw_df.sort_values(by='net_pnl',ascending=False)
    top_record = final_df.head(1)
    top_record_dict = final_df.iloc[0].to_dict()  
    
    
    ##fetch the corresponsing fields of top_row
    pnl = top_record_dict['net_pnl']
    wins = top_record_dict['total_wins']
    losses = top_record_dict['total_losses'] 
    opt_param = {'max_loss_p': float(top_record_dict['max_loss_p']),
                 'risk_reward': float(top_record_dict['risk_reward'])}
    opt_param_json = json.dumps(opt_param)
    timeframe = top_record_dict['timeframe']
    
    ##Put the result in dictionary format
    result = {"dataframe":[top_record,final_df],
              "pnl":pnl,
              "wins":wins,
              "losses":losses,
              "opt_params": opt_param_json,
              "timeframe": timeframe
              }
    
    
    return result


def getResults(symbol,strategy_obj, timeframe, run_loop_done,opt_mode):
   
    # add analyzers
    add_analyzers(strategy_obj)
    
    # run backtest
    try:
        results = strategy_obj.run()
    except Exception as err:
        print(f"!!!!!!!!!!!!!Error for symbol {symbol}!!!!!!!!!!!!!")
        print(err)
        return
        
    global all_results
    # collect results
    if opt_mode == 1:   
        results = collect_results_opt(results,timeframe)
        all_results[timeframe] = results

        
    else:
        results = collect_results(results,timeframe)
    
    metrics = {}
    if(run_loop_done):
        metrics = CompareResults(all_results)
        info = generate_payload(symbol=symbol, metrics=metrics, opt_mode=opt_mode)
        # for i in info.keys():
            # print(i)
        database = db()
        database.update_results(info)
        

    
    
    
    
