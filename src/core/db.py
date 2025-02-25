import psycopg2 
import pandas.io.sql as sqlio
import boto3
import json

region_name = 'ap-south-1'
ssm = boto3.client('ssm',region_name=region_name)

class Database:
    
    def __init__(self):
        self.conn = self.establishConnection()
    
    def establishConnection(self):
        db_config = self.__timescaledb_credentials()
        try:
            conn = psycopg2.connect(
                database=db_config['database'],
                user=db_config['user'],
                password=db_config['password'],
                host=db_config['host'],
                port=db_config['port'],
            )
            print("✅ Connection to the Timescale PostgreSQL established successfully.")
            return conn
        except Exception as e:
            print("❌ Connection to the Timescale PostgreSQL encountered an error: ", e)
            return None
        
    
    def __timescaledb_credentials(self):
        parameter = ssm.get_parameter(Name='timescaledb_credentials', WithDecryption=True)
        timescaledb_config = json.loads(parameter['Parameter']['Value'])
        return timescaledb_config
        
    def get_data_frame(self,query):
        
        pandas_df = sqlio.read_sql_query(query, self.conn)        
        return pandas_df
    
    def update_results(self,data):
        # data['strategy_id']
        # data['test_date'] = today
        # data['symbol'] = 
        # data['payload'] = 
        # insert data into backtests table
        print(data)
        query = """
        INSERT INTO backtests (test_id, symbol, strategy_id, run_time, payload_all, wins, net_pnl, loses)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (test_id) 
        DO UPDATE SET 
            symbol = EXCLUDED.symbol,
            strategy_id = EXCLUDED.strategy_id,
            run_time = EXCLUDED.run_time,
            payload_all = EXCLUDED.payload_all,
            wins = EXCLUDED.wins,
            net_pnl = EXCLUDED.net_pnl,
            loses = EXCLUDED.loses; 
        """
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, (
                    data[0],   # test_id
                    data[1],   # symbol
                    data[2],   # strategy_id
                    data[3],   # run_time
                    data[4],   # value_base64 (payload_all)
                    float(data[5]),   # wins
                    float(data[6]),   # net_pnl
                    float(data[7])   # losses
                ))
                self.conn.commit()
                print("✅ Data inserted successfully!")
        except Exception as e:
            print("❌ Error inserting data:", e)
        
        