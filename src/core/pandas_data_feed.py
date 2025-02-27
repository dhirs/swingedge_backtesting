import backtrader as bt
from src.core.db import Database


class PandasData(bt.feeds.PandasData):
    params = (
        ('datetime', 'bucket'),
        ('open', -1),
        ('high', -1),
        ('low', -1),
        ('close', -1),
        ('volume', -1),
    )

def get_data_feed(query):
    
    data_feed = None
    db = Database()
    query_results_data_frame = db.get_data_frame(query)
    
    if not query_results_data_frame.empty:
        data_feed = PandasData(dataname=query_results_data_frame)   
    
    return data_feed