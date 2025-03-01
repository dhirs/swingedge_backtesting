import psycopg2 
import pandas.io.sql as sqlio
import boto3
import json
from psycopg2.extras import execute_values

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
            # print("✅ Connection to the Timescale PostgreSQL established successfully.")
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
    

    def update_results(self, data):
        # print(data.keys())
    
        if not data:
            print("⚠️ No data provided for insertion.")
            return

        query = """
            INSERT INTO backtests (symbol, strategy_id, run_time, payload_all, payload_best, opt_params,sort_by,batch_id)
            VALUES %s
            ON CONFLICT (test_id) 
            DO UPDATE SET 
                symbol = EXCLUDED.symbol,
                strategy_id = EXCLUDED.strategy_id,
                run_time = EXCLUDED.run_time,
                payload_all = EXCLUDED.payload_all,
                payload_best = EXCLUDED.payload_best,
                opt_params = EXCLUDED.opt_params,
                sort_by = EXCLUDED.sort_by,
                batch_id = EXCLUDED.batch_id
        """

       
        values = [(
        data.get('symbol'),
        data.get('strategy_id'),
        data.get('run_time'),
        data.get('payload_all_base64'),   
        data.get('payload_best_base64'),   
        data.get('opt_params'),
        'pnl',
        1
        )]



        try:
            with self.conn.cursor() as cursor:
                execute_values(cursor, query, values)
                self.conn.commit()
                print(f"✅ Successfully inserted/updated {len(values)} record(s).")
        except Exception as e:
            # self.conn.rollback()  
            print("❌ Error inserting data:", e)
        finally:
            self.conn.close()

            
            