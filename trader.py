import pandas as pd
import numpy as np
from pathlib import Path
import os
import time
import seaborn as sns
import datetime

sns.set_theme()
cd = Path(os.path.curdir)

df = pd.read_csv(cd / 'stock_history.csv', index_col='date')
df.index = pd.to_datetime(df.index)

TICKERS = ['SBUX', 'CMG', 'TREC', 'MCD', 'AAPL', 'WEN', 'F']

"""Probably add some sort of portfolio class with which just be used to convey info about trader's holdings."""


class Trader:
    """Total portfolio which should have positions"""

    # pie graph of position percentages

    cash: float = 0
    positions = []

    def __init__(self, initial_cash=0, positions=[]):
        self.cash = initial_cash
        self.positions = positions

    def value(self):
        """Current portfolio Value"""
        pass

    def __repr__(self):
        return str(self.positions)


class Security:
    """Class to model a security"""

    def __init__(self, ticker: str):
        self.ticker = ticker

    @property
    def ticker(self):
        return self._ticker

    @ticker.setter
    def ticker(self, value: str):
        self._ticker = value.upper()


class Stock(Security):
    """Inherits from Security class"""


class Position:
    """Must have """
    # I think that the below creates class attributed when they are all just instance attributes, but I want to be able
    # to glance at this class and see the relevant variables that each instance has.

    _trade: str
    security: Security
    enter_date: datetime.datetime
    exit_date: datetime.datetime
    quantity: float
    closed: bool = False

    def __init__(self, trade_type: str, quantity: float, enter_date: datetime.datetime,
                 security: Security):

        self.trade_type = trade_type
        self.quantity = float(quantity)
        self.enter_date = enter_date
        self.security = security

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

    def __str__(self):
        return f'Ticker:{self.security.ticker}\Type:{self.trade_type}\nQuantity:{self.quantity}'

    def __repr__(self):
        return self.security.ticker

# def make_trade()
