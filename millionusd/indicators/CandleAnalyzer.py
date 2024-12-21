import numpy as np
import talib


class CandleAnalyzer:
    def __init__(self, candle, all_candles):
        self.candle = candle
        self.all_candles = all_candles

    def get_prices(self):
        return [c.close_price for c in self.all_candles]

    def get_volumes(self):
        return [c.volume for c in self.all_candles]

    def get_highs(self):
        return [c.max_price for c in self.all_candles]

    def get_lows(self):
        return [c.min_price for c in self.all_candles]

    def calculate_sma(self, period):
        prices = self.get_prices()
        return talib.SMA(np.array(prices), timeperiod=period)

    def calculate_ema(self, period):
        prices = self.get_prices()
        return talib.EMA(np.array(prices), timeperiod=period)

    def calculate_macd(self, short_period=12, long_period=26, signal_period=9):
        prices = self.get_prices()
        macd, signal, hist = talib.MACD(np.array(prices), fastperiod=short_period, slowperiod=long_period,
                                        signalperiod=signal_period)
        return macd, signal

    def calculate_rsi(self, period=14):
        prices = self.get_prices()
        return talib.RSI(np.array(prices), timeperiod=period)

    def calculate_bollinger_bands(self, period=20, num_std_dev=2):
        prices = self.get_prices()
        upperband, middleband, lowerband = talib.BBANDS(np.array(prices), timeperiod=period, nbdevup=num_std_dev,
                                                        nbdevdn=num_std_dev, matype=0)
        return upperband, middleband, lowerband

    def calculate_atr(self, period=14):
        highs = self.get_highs()
        lows = self.get_lows()
        closes = self.get_prices()
        return talib.ATR(np.array(highs), np.array(lows), np.array(closes), timeperiod=period)

    def calculate_stochastic_oscillator(self, period=14):
        highs = self.get_highs()
        lows = self.get_lows()
        closes = self.get_prices()
        slowk, slowd = talib.STOCHF(np.array(highs), np.array(lows), np.array(closes), fastk_period=period)
        return slowk, slowd

    def calculate_fibonacci_retracement(self, high, low):
        diff = high - low
        return {
            "level_0.0": high,
            "level_0.236": high - 0.236 * diff,
            "level_0.382": high - 0.382 * diff,
            "level_0.618": high - 0.618 * diff,
            "level_1.0": low
        }

    def calculate_total_volume(self):
        return np.sum(self.get_volumes())

    def calculate_cci(self, period=20):
        highs = np.array([c.max_price for c in self.all_candles])
        lows = np.array([c.min_price for c in self.all_candles])
        closes = np.array([c.close_price for c in self.all_candles])
        cci = talib.CCI(highs, lows, closes, timeperiod=period)
        return cci

    def calculate_adx(self, period=14):
        highs = self.get_highs()
        lows = self.get_lows()
        closes = self.get_prices()
        return talib.ADX(np.array(highs), np.array(lows), np.array(closes), timeperiod=period)

    def calculate_obv(self):
        prices = np.array([c.close_price for c in self.all_candles], dtype=np.float64)
        volumes = np.array([c.volume for c in self.all_candles], dtype=np.float64)
        obv = talib.OBV(prices, volumes)
        return obv

    def calculate_mfi(self, period=14):
        highs = np.array([c.max_price for c in self.all_candles], dtype=np.float64)
        lows = np.array([c.min_price for c in self.all_candles], dtype=np.float64)
        closes = np.array([c.close_price for c in self.all_candles], dtype=np.float64)
        volumes = np.array([c.volume for c in self.all_candles], dtype=np.float64)
        mfi = talib.MFI(highs, lows, closes, volumes, timeperiod=period)
        return mfi

    def calculate_trix(self, period=15):
        prices = self.get_prices()
        return talib.TRIX(np.array(prices), timeperiod=period)

    def calculate_williams_r(self, period=14):
        highs = self.get_highs()
        lows = self.get_lows()
        closes = self.get_prices()
        return talib.WILLR(np.array(highs), np.array(lows), np.array(closes), timeperiod=period)

    def calculate_ultimate_oscillator(self, short_period=7, medium_period=14, long_period=28):
        highs = self.get_highs()
        lows = self.get_lows()
        closes = self.get_prices()
        return talib.ULTOSC(np.array(highs), np.array(lows), np.array(closes), timeperiod1=short_period,
                            timeperiod2=medium_period, timeperiod3=long_period)
