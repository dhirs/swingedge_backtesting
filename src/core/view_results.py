# -*- coding: utf-8 -*-
"""JSONVisualizer

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/12OSlbmQ5Cz9zhKymqu2QYjhmJeMfV4Nm
"""

!pip install boto3
!pip install tabulate
!pip install psycopg2

import boto3, json, psycopg2
import pandas.io.sql as sqlio
import pandas as pd
import base64
from tabulate import tabulate
import warnings
warnings.filterwarnings('ignore')

from google.colab import userdata
key = userdata.get('AWS_KEY')
secret = userdata.get('AWS_SECRET')

region = "ap-south-1"
ssm = boto3.client('ssm', aws_access_key_id=key,  aws_secret_access_key=secret, region_name=region)
parameter = ssm.get_parameter(Name='timescaledb_credentials', WithDecryption=True)
config = json.loads(parameter['Parameter']['Value'])

conn = psycopg2.connect(database = config['database'],
                         user =  config['user'],
                         password = config['password'],
                         host = config['host'],
                         port = config['port'],
        )

def get_data(test_id, node_name):
  query = f"select * from backtests where test_id = {test_id}"
  data = sqlio.read_sql_query(query,conn)
  df = pd.DataFrame(data)
  val = df['payload_best'][0]
  base64_bytes = val.encode("ascii")
  sample_string_bytes = base64.b64decode(base64_bytes)
  json_payload = sample_string_bytes.decode("ascii")
  data = json.loads(json_payload)
  # print(data)
  return data[0][node_name],data

test_id = 103

sharpe,all = get_data(test_id, 'sharpe')
print(sharpe)
# print(all)

returns,all = get_data(test_id, 'returns')
df = pd.DataFrame([returns])
print(df)

drawdown,all = get_data(test_id, 'drawdown')
# df = pd.DataFrame([drawdown])
pd.json_normalize(drawdown)
# print(df)

def get_trades(test_id):

  trades,all= get_data(test_id, 'trades')
  df = pd.json_normalize(trades)
  df_all = pd.json_normalize(all)
  df_final = pd.DataFrame(
      [
        [
            all[0]['timeframe'] ,
            all[0]['max_loss_p'],
            all[0]['risk_reward'],

            df['won.total'][0]/(df['won.total'][0]+df['lost.total'][0]),

            df['won.pnl.total'][0]+df['lost.pnl.total'][0],

            100*df['long.won'][0]/(   df['long.won'][0]  +df['long.lost'][0]  ),

            100*df['short.won'][0]/(   df['short.won'][0]  +df['short.lost'][0]),
            df['len.average'][0]

        ]

      ],
      columns=['Timeframe','MaxLossP','RiskReward','WinRatio',
               'NetRevenue',
               'LongWinP',
               'ShortWinP',
               'AvTime'])
  return df_final
  # print(df.columns)
  # print(df_all)
  # print(f"Timeframe:{all[0]['timeframe']}")
  # print(f"Total wins:{df['won.total'][0]}")
  # print(f"Total losses:{df['lost.total'][0]}")
  # win_ratio = df['won.total'][0]/(df['won.total'][0]+df['lost.total'][0])
  # print(f"Win ratio:{win_ratio}")
  # print(f"Gross revenue:{df['won.pnl.total'][0]}")
  # print(f"Gross loss:{df['lost.pnl.total'][0]}")
  # print(f"Net revenue:{df['won.pnl.total'][0]+df['lost.pnl.total'][0]}")
  # print(f"Long wins:{df['long.won'][0]}")
  # print(f"Long losses:{df['long.lost'][0]}")
  # print(f"Long win%:{100*df['long.won'][0]/(   df['long.won'][0]  +df['long.lost'][0]  )  })")
  # print(f"Short wins:{df['short.won'][0]}")
  # print(f"Short losses:{df['short.lost'][0]}")
  # print(f"Short win%:{100*df['short.won'][0]/(   df['short.won'][0]  +df['short.lost'][0]  )  })")
  # print(f"Avg. trade length:{df['len.average'][0]}")

transactions,all = get_data(test_id, 'transactions')
# print(transactions)
table_data = []
for timestamp, transactions_list in transactions.items():
    for index, transaction in enumerate(transactions_list):
        row = [timestamp, index] + transaction
        table_data.append(row)
headers = ["Timestamp", "Transaction ID", "0", "1", "2", "3", "4"]
print(tabulate(table_data, headers=headers, tablefmt="grid"))

from IPython.display import display

def generate_combined_results(strategy_id,sort_field):
  query = f"select test_id, symbol,payload_best from backtests where strategy_id = {strategy_id}"
  data = sqlio.read_sql_query(query,conn)
  df = pd.DataFrame(data)
  frames = []
  for index, row in df.iterrows():
      test_id = row['test_id']
      stats = get_trades(test_id)
      stats.insert(0, 'Symbol', row['symbol'])
      frames.append(stats)
  final = pd.concat(frames)
  display(final.sort_values(by=sort_field, ascending=[False]))

strategy_id = 1
sort_field = 'NetRevenue'
generate_combined_results(strategy_id,sort_field)