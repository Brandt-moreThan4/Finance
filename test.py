import pandas as pd
import numpy as np
from pathlib import Path
import os
import time
import seaborn as sns
import datetime
import random as rd
from copy import deepcopy

from trader import *


dut = datetime.datetime(2007, 1, 5)
exit_dut = datetime.datetime(2009, 1, 5)

port = Trader(1_000_000)

sbux = Stock('sbux')

trade = Position('long', 50, dut, sbux)
trade.exit_date = exit_dut
port.positions.append(trade)

# print(df[port.positions[0].ticker].loc[port.positions[0].enter_date])
# print(df[port.positions[0].ticker].loc[port.positions[0].exit_date])

porty = port
port2 = deepcopy(port)


print('lol')