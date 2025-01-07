from typing import List
from collections import defaultdict

import numpy as np


class Candle:
    def __init__(self, start_time=None, end_time=None, open_price=None, close_price=None, max_price=None, min_price=None, volume=None):
        self.start_time = start_time
        self.end_time = end_time
        self.open_price = open_price
        self.close_price = close_price
        self.max_price = max_price
        self.min_price = min_price
        self.volume = volume

    def __repr__(self):
        return f"Candle(start_time={self.start_time}, end_time={self.end_time}, open_price={self.open_price}, close_price={self.close_price}, max_price={self.max_price}, min_price={self.min_price}, volume={self.volume})"

    def read(self, candles):
        inputs = {
            'open': np.array([]),
            'high': np.array([]),
            'low': np.array([]),
            'close': np.array([]),
            'volume': np.array([]),
            'from': np.array([]),
            'at': np.array([]),
            'to': np.array([])
        }

        for timestamp in list(candles):
            inputs["open"] = np.append(inputs["open"], candles[timestamp]["open"])
            inputs["high"] = np.append(inputs["high"], candles[timestamp]["max"])
            inputs["low"] = np.append(inputs["low"], candles[timestamp]["min"])
            inputs["close"] = np.append(inputs["close"], candles[timestamp]["close"])
            inputs["volume"] = np.append(inputs["volume"], candles[timestamp]["volume"])
            inputs["from"] = np.append(inputs["from"], candles[timestamp]["from"])
            inputs["at"] = np.append(inputs["at"], candles[timestamp]["at"])
            inputs["to"] = np.append(inputs["to"], candles[timestamp]["to"])
        return inputs