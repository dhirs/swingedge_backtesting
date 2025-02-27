params = {'max_loss_p':'range(1,4,1)', 
              'risk_reward' :'range(1,8,1)'}
strategy_class = 'BaseStrategy'

list = []
for key, value in params.items():
    list.append(f"{key} = {value}")
    
final_str = strategy_class + ","+",".join(list)
print(final_str)