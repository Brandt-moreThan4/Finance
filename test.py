"""This file is just the play thing to test the code and experiment."""

from trader import *

tp = TradingPit()
taleb = Trader(initial_cash=1_000_000)
tp.traders.append(taleb)


def taleb_rule(yesterday, today):
    """Buy if the price today is higher than it was yesterday."""
    if today > yesterday:
        return True
    else:
        return False


sbux = Stock('sbux')

for i in range(1, len(tp.trade_dates)):

    yesterday_price = sbux.df[sbux.ticker].iloc[i - 1]
    today_price = sbux.df[sbux.ticker].iloc[i]
    if today_price > yesterday_price:
        position = Position('long', 1, tp.trade_dates[i], sbux)
        taleb.current_positions.append(position)

print('lol')
