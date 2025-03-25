import src.core.base_strategy as BaseStrategy
import backtrader as bt

class MACD(BaseStrategy):
  
    params = (
       
        ('max_loss_p' , 1),
        ('risk_reward', 9),
        ('size',0.005)
          
    )
    
 
    def __init__(self):
        super().__init__()
        self.macd = bt.indicators.MACD(self.data.close)
        self.mcross = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)
   
       
    def get_long_entry(self):
            
      if self.mcross[0] > 0.0:                                
      
        if self.macd.macd[0] < 0 and self.macd.signal[0] < 0:
          return True
    
    def get_long_exit(self):
      # stop_price = self.execution_price*(1-self.params.max_loss_p/100)
      # if self.data.close[0] < stop_price:
      if self.data.close[0] < self.low:
        return True
      
      target_price = self.execution_price*(1+ self.params.risk_reward/100)
      if self.data.close[0] >= target_price:
        return True
    
    def get_short_entry(self):
      if self.mcross[0] < 0.0:  
        if self.macd.macd[0] > 0 and self.macd.signal[0] > 0:
          return True
        
    
    def get_short_exit(self):
      # stop_price = self.execution_price *(1+self.params.max_loss_p/100)
      # if self.data.close[0] > stop_price:
      if self.data.close[0] > self.high:
        return True
      
      target_price = self.execution_price*(1-self.params.risk_reward/100)
      if self.data.close[0] <= target_price:
        return True
    
 

    
    