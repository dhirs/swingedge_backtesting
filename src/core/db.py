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
    
    def update_results(self, symbol, data, opt_mode = None):
        # data['strategy_id']
        # data['test_date'] = today
        # data['symbol'] = 
        # data['payload'] = 
        # insert data into backtests table
        print("all done-------------------------")
        pass