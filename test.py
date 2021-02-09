import pandas as pd
import numpy as np
from pathlib import Path
import os
import time
import seaborn as sns
import datetime
import random as rd

from trader import *

# for ticker in TICKERS:
#     stock = Stock(ticker)
#     positions.append(Position('long',
#                                      rd.randint(1, 10),
#                                      datetime.date.today(),
#                                      stock))


# p = Portfolio(1_000_000, positions=positions)
# print(p.positions)

dut = datetime.datetime(2007, 1, 5)
exit_dut = datetime.datetime(2009, 1, 5)

port = Portfolio(1_000_000)

sbux = Stock('sbux')

trade = Position('long', 50, dut, sbux)
trade.exit_date = exit_dut
port.positions.append(trade)

print(df[port.positions[0].ticker].loc[port.positions[0].enter_date])
print(df[port.positions[0].ticker].loc[port.positions[0].exit_date])
