import json
import fxcm_rest_api_token as fxcm_rest_api
import time
import sys
from pyti.exponential_moving_average import exponential_moving_average as ema
from pyti.relative_strength_index import relative_strength_index as RSI
from pyti.bollinger_bands import middle_bollinger_band as BBbasis

# Connection
trader = fxcm_rest_api.Trader('ae14cfd5becad3099169673a05d66944427dd5d6', 'demo')
# Testing account
#trader = fxcm_rest_api.Trader('caea1e883e091969ea76667fdf735251cfd83028', 'demo')

trader.login()


# Get number of open position
def get_open_position():
    positions = trader.get_model("OpenPosition")['open_positions']
    if positions[0]['tradeId'] == '':
        return 0
    else:
        return(len(positions)-1)



# Get only closed price forn FXCM candle
def get_closed_price(data):
    closedPrice = []
    for period in data:
        closedPrice.append(period[2])
    return closedPrice


# Strategie
def  buy_or_sell(data):
    slowEMA = ema(data, 75)
    fastEMA = ema(data, 5)
    sma = BBbasis(data, 20)
    rsi = RSI(data, 21)
    

    # Buy
    if sma[len(sma)-1]<data[len(data)-1] and slowEMA[len(slowEMA)-1]<data[len(data)-1] and slowEMA[len(slowEMA)-1]<fastEMA[len(fastEMA)-1] and rsi[len(rsi)] > 50:
        print('Decision => BUY')
        return True
    # Short
    elif sma[len(sma)-1]>data[len(data)-1] and slowEMA[len(slowEMA)-1]>data[len(data)-1] and slowEMA[len(slowEMA)-1]>fastEMA[len(fastEMA)-1] and rsi[len(rsi)] < 50:
        print('Decision => SHORT')
        return False
    # Nothing
    else:
        print('Decision => Do nothing')
        return 42


# Make order on FXCM
def make_order(decision, data, account_id):
    if decision != 42:
        return(trader.open_trade(account_id=trader.account_id, symbol="EUR/USD", is_buy=decision, amount=250, trailing_step=10, limit=200, stop=-100, is_in_pips=True))
    return

try:
    print("Logged in, now getting Account details")
    while len(trader.account_list) < 1:
           time.sleep(0.1)
    account_id = trader.account_list[0]
    while (True):
        open_pos = get_open_position()
        print("Number of open position: ", open_pos)
        # Limit pyramiding order to 2
        if open_pos < 2:
            candle = trader.candles(1, "H1", 75)['candles']
            data = get_closed_price(candle)
            decision = buy_or_sell(data)
            order = make_order(decision, data, account_id)
            print(order)
        time.sleep(3600)
except Exception as e:
    print(str(e))
