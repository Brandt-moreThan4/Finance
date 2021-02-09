import pandas as pd
from pathlib import Path
import os
import datetime

cd = Path(os.path.curdir)

df = pd.read_csv(cd / 'stock_history.csv', index_col='date')
df.index = pd.to_datetime(df.index)

TICKERS = ['SBUX', 'CMG', 'TREC', 'MCD', 'AAPL', 'WEN', 'F']

"""Probably add some sort of portfolio class with which just be used to convey info about trader's holdings."""


# pie graph of position percentages


class Trader:
    """Total portfolio which should have positions"""

    def __init__(self, initial_cash=0, positions=[]):
        self.cash = initial_cash
        self.current_positions = positions
        self.closed_positions: list = []

    def value(self):
        """Current portfolio Value"""

    def __repr__(self):
        return str(self.current_positions)


class Security:
    """Class to model a security"""
    df: pd.DataFrame = df

    def __init__(self, ticker: str):
        self.ticker = ticker

    @property
    def ticker(self):
        return self._ticker

    @ticker.setter
    def ticker(self, value: str):
        self._ticker = value.upper()

    def get_price(self, date_time: datetime.datetime):
        """Looks up the price in a panda dataframe. Assumes that the pd df has column of this security ticker"""
        price = df[self.ticker].loc[date_time]
        return price


class Stock(Security):
    """Inherits from Security class"""


class Position:
    """Can be either closed or open. """

    def __init__(self, trade_type: str, quantity: float, enter_date: datetime.datetime,
                 security: Security):

        self.trade_type = trade_type
        self.quantity = float(quantity)
        self.enter_date = enter_date
        self.security = security
        self.enter_price = self.security.get_price(self.enter_date)

        # Below are never provided on creation. Is there a better way to do this?
        self.closed = False
        self.exit_date = None
        self.exit_price = None

    @property
    def ticker(self):
        return self.security.ticker

    @property
    def trade_type(self):
        return self._trade_type

    @trade_type.setter
    def trade_type(self, value: str):
        if value.upper() == 'LONG' or value.upper() == 'SHORT':
            self._trade_type = value.upper()
        else:
            raise Exception('Sorry bro. trade_type can only be long or short.')

    def close(self, exit_date: datetime.datetime):
        """Close out the position"""
        self.exit_price = self.security.get_price(exit_date)
        self.exit_date = exit_date
        self.closed = True

    def __str__(self):
        return f'Ticker:{self.security.ticker}\nType:{self.trade_type}\nQuantity:{self.quantity}'

    def __repr__(self):
        return self.security.ticker

