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

from tabulate import tabulate
warnings.filterwarnings('ignore')

pd.set_option('display.max_columns',None)
all_results = {}


def get_data_other(timeframe, symbol, asset_class):
    
    prefix = 'cr'
    if asset_class == 'index':
        prefix  = 'idx'
    
    if timeframe == '15m':
        table_name = 'fifteen_m'
        
    elif timeframe == '30m':
        table_name = 'thirty_m'
        
    elif timeframe == '45m':
        table_name = 'fortyfive_m'
        
    elif timeframe == '1h':
        table_name = 'one_h'
    
    elif timeframe == '4h':
        table_name = 'four_h'
        
    elif timeframe == '1d':
        table_name = 'daily'
   
        
    elif timeframe == '1w':
        table_name = 'weekly'
        
    elif timeframe == '1m':
        table_name = 'monthly'
        
    final_table_name = prefix + "_" + table_name
    print(final_table_name)
    
    query = f"select * from {final_table_name} where symbol = '{symbol}' and extract(DOW from bucket) between 1 and 5 order by bucket asc"
    # query = "select * from cr_daily where DATE(bucket) between '2024-09-16' and '2024-09-25' order by bucket asc"
    data_feed = pdf.get_data_feed(query)
    
    if data_feed is None:
        print(f"!!!!!!!!!No data found for {symbol}, in timeframe {timeframe}!!!!!!")
    else:
        print(f"-----Found data for {symbol},{timeframe}-----")
        
    return data_feed

    
def get_data(timeframe, symbol,asset_class):
    
    if asset_class in ['crypto' , 'index']:
        return get_data_other(timeframe, symbol, asset_class)
    
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
    if data_feed is None:
        print(f"!!!!!!!!!No data found for {symbol}, in timeframe {timeframe}!!!!!!")
    else:
        print(f"-----Found data for {symbol},{timeframe}-----")
        
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
    try: 
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
    
    except Exception as err:
        print(f"!!!!!!Error populating results for {timeframe}!!!!!!!!")
        print(err)
        return pd.DataFrame()
    
    
    return resultDf
    
       
def collect_results(results,timeframe):
    try:
        sharpe = results[0].analyzers.sharpe.get_analysis()
        drawdown = results[0].analyzers.drawdown.get_analysis()
        trades = results[0].analyzers.trades.get_analysis()
        rets = results[0].analyzers.returns.get_analysis()
        transactions = results[0].analyzers.transactions.get_analysis()
        
        n_trades = len(transactions)
        if n_trades == 0 or n_trades == 1:
            print("!!!!!!!!!!!Not enough transactions!!!!!!!!!!!")
            return pd.DataFrame()
    
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
    
    except Exception as err:
        print(f"!!!!!!Error populating results for {timeframe}!!!!!!!!")
        print(err)
        return pd.DataFrame()
    
    return df


def generate_payload(strategy_id, symbol,metrics,opt_mode):
    if opt_mode==1:
        
        run_time = datetime.now(timezone.utc)
        
        df_json = metrics['dataframe'][1].to_json(orient="records", indent=4)
        df_base64 = base64.b64encode(df_json.encode()).decode()
        best_result_json = metrics['dataframe'][0].to_json(orient="records", indent=4)
        best_base64 = base64.b64encode(best_result_json.encode()).decode()
        
        
        metrics['payload_all_base64'] = df_base64
        metrics['payload_best_base64'] = best_base64
        metrics['run_time'] = run_time
        metrics['strategy_id'] = strategy_id
        metrics['symbol'] = symbol
        return metrics
        
        
       
    else:
        
        run_time = time.time()
        metrics_json = metrics.to_json(orient="records") 
                
        payload = {
            "symbol": symbol,
            "strategy": strategy_id,
            "run_time": run_time,
            "metrics": metrics_json
        }


        metrics_list = json.loads(payload["metrics"]) 
        df_expanded = pd.DataFrame(metrics_list)
        df_expanded["symbol"] = payload["symbol"]
        df_expanded["strategy"] = payload["strategy"]
        df_expanded["run_time"] = payload["run_time"]

        df_compact = pd.DataFrame([payload])  

        # for key,value in payload.items():
        #     print(f"key: {key} | value: {value}")
        

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


def getResults(symbol,strategy_obj, timeframe, run_loop_done,opt_mode,save_mode=0):
    
    # get strategy id
    strategy_id  = strategy_obj.id
    
    # add analyzers
    add_analyzers(strategy_obj)
    
    # run backtest
    try:
        results = strategy_obj.run()
        
        
    except Exception as err:
        print(f"!!!!!!!!!!!!!Error running strategy for symbol {symbol}!!!!!!!!!!!!!")
        print(err)
        return
        
    global all_results
    # collect results
    if opt_mode == 1:   
        results = collect_results_opt(results,timeframe)
        if not results.empty:
            all_results[timeframe] = results
            
            print(f"--------Strategy ran successfully for {symbol}, {timeframe}---------")
        else:
            print(f"!!!!!!!No results, strategy not run for {symbol}, {timeframe}!!!!!!!")

        
    else:
        results = collect_results(results,timeframe)
    
    metrics = {}
    if(run_loop_done):
        metrics = CompareResults(all_results)
        info = generate_payload(strategy_id,symbol=symbol, metrics=metrics, opt_mode=opt_mode)
        # for i in info.keys():
            # print(i)
        if save_mode == 1:
            database = db()
            database.update_results(info)
        else:
            print(metrics)
        

    
    
def display_results(results,tf):
        final = collect_results(results,tf)
        
        if not final.empty:
               
            columns_to_print = ['net_profit', 'win_ratio','long_wins','long_losses','short_wins','short_losses']
            print("Summary")
            print(tabulate(final[columns_to_print], headers='keys', tablefmt='psql'))
    
    
