import backtrader as bt
from src.core.corestrategy import CoreStrategy

class MACDStrategy(CoreStrategy):
  
    params = (
       
        ('max_loss_p' , 1),
        ('risk_reward', 3),
        ('size',0.5)
          
    )
   
 
    def __init__(self):
        
        super().__init__(self.params)
        self.macd = bt.indicators.MACD(self.data.close)
        self.mcross = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)
               
       
    def get_long_entry(self):
            
      if self.mcross[0] > 0.0:                                
      
        if self.macd.macd[0] < 0 and self.macd.signal[0] < 0:
          return True
    
    def get_long_exit(self):
      max_risk  = self.execution_price*self.params.max_loss_p
      stop_price = self.execution_price - max_risk
      # if self.data.close[0] < self.low:
      if self.data.close[0] < stop_price:
        return True
      
      target_price = self.execution_price*(1+ self.params.risk_reward/100)
      if self.data.close[0] >= target_price:
        return True
    
    def get_short_entry(self):
      if self.mcross[0] < 0.0:  
        if self.macd.macd[0] > 0 and self.macd.signal[0] > 0:
          return True
        
    
    def get_short_exit(self):
      max_risk  = self.execution_price*self.params.max_loss_p
      stop_price = self.execution_price + max_risk
      if self.data.close[0] > stop_price:
      # if self.data.close[0] > self.high:
        return True
      
      target_price = self.execution_price*(1-self.params.risk_reward/100)
      if self.data.close[0] <= target_price:
        return True
 
 

    
    