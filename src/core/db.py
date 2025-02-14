import psycopg2 as db
import pandas.io.sql as sqlio


class Database:
    
    def __init__(self, params=None):
        
        db_username = 'tsdbadmin'
        db_password = 'letin1234$Agf'
        db_url = 'jdbc:postgresql://w25uxmcny6.m8iecjpjs8.tsdb.cloud.timescale.com:30127/tsdb'
        db_host = 'w25uxmcny6.m8iecjpjs8.tsdb.cloud.timescale.com'
        db_ = 'tsdb'
        db_port = 30127
        self.conn = db.connect(
        database=db_,
        user=db_username,
        password=db_password,
        host=db_host,
        port=db_port)
        
    def get_data_frame(self,query):
        
        pandas_df = sqlio.read_sql_query(query, self.conn)
        print(pandas_df)
        return pandas_df
    
    