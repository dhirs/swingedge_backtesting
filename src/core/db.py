import psycopg2 as db
import pandas.io.sql as sqlio


class Database:
    
    def __init__(self, params=None):
        
        db_username = 'postgres'
        db_password = 'ytu6R5647yadg4@'
        db_url = 'jdbc:postgresql://13.201.206.183:5432/postgres'
        db_host = '13.201.206.183'
        db_ = 'postgres'
        db_port = 5432
        self.conn = db.connect(
        database=db_,
        user=db_username,
        password=db_password,
        host=db_host,
        port=db_port)
        
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
                print("✅ Data inserted successfully!")
        except Exception as e:
            print("❌ Error inserting data:", e)
        
        