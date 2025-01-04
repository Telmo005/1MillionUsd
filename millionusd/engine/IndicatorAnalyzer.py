import numpy as np
import talib


class IndicatorAnalyzer:
    def __init__(self, all_candles):
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

    def identify_moving_average_convergence(self, short_period=5, medium_period=10, long_period=21):
        """
        Identifica o último cruzamento das médias móveis e retorna a tendência (alta/baixa) e o número de candles após o cruzamento.

        :param short_period: Período da média móvel curta (exemplo: 5)
        :param medium_period: Período da média móvel intermediária (exemplo: 10)
        :param long_period: Período da média móvel longa (exemplo: 21)
        :return: Último cruzamento e a quantidade de candles após o cruzamento
        """
        # Calcula as médias móveis exponenciais para os períodos fornecidos
        ema_short = self.calculate_ema(short_period)
        ema_medium = self.calculate_ema(medium_period)
        ema_long = self.calculate_ema(long_period)

        last_crossover = None  # Para armazenar o último cruzamento
        last_trend = None  # Para armazenar a tendência (alta/baixa)

        # Itera sobre os índices das EMAs para encontrar os cruzamentos
        for i in range(1, len(ema_short)):
            # Verifica se ocorreu um cruzamento para cima (tendência de alta)
            if ema_short[i] > ema_medium[i] > ema_long[i] and not (
                    ema_short[i - 1] > ema_medium[i - 1] > ema_long[i - 1]):
                last_crossover = (i, "Cross Up")  # Último cruzamento para cima
                last_trend = "Alta"

            # Verifica se ocorreu um cruzamento para baixo (tendência de baixa)
            elif ema_short[i] < ema_medium[i] < ema_long[i] and not (
                    ema_short[i - 1] < ema_medium[i - 1] < ema_long[i - 1]):
                last_crossover = (i, "Cross Down")  # Último cruzamento para baixo
                last_trend = "Baixa"

        # Verifica se encontrou um cruzamento
        if last_crossover:
            # Conta os candles após o último cruzamento
            crossover_index = last_crossover[0]
            candles_after_cross = len(ema_short) - crossover_index - 1
            return last_trend, candles_after_cross
        else:
            return None, 0  # Caso não haja cruzamento encontrado

    def identify_sideways_market(self, medium_period=10, long_period=21, threshold=12):
        """
        Identifica se o mercado está lateralizado baseado no número de candles
        que tocam ambas as médias móveis fornecidas.

        :param medium_period: Período da média móvel intermediária (exemplo: 10).
        :param long_period: Período da média móvel longa (exemplo: 21).
        :param threshold: Número mínimo de candles tocando as médias para considerar lateralização.
        :return: True se o mercado estiver lateralizado, False caso contrário.
        """
        # Calcula as médias móveis para os períodos fornecidos
        ema_medium = self.calculate_ema(medium_period)
        ema_long = self.calculate_ema(long_period)
        candles = self.all_candles

        touch_count = 0

        for i in range(max(medium_period, long_period), len(candles)):
            candle = candles[i]
            candle_high = candle.max_price
            candle_low = candle.min_price

            # Verifica se o corpo do candle toca ambas as médias móveis
            if candle_low <= ema_medium[i] <= candle_high and candle_low <= ema_long[i] <= candle_high:
                touch_count += 1

            # Retorna True assim que o número de toques atinge o limite
            if touch_count >= threshold:
                return True

        return False

    def validate_moving_average_alignment(self, ema_periods=(5, 10, 21), min_distance=0.1):
        """
        Valida o alinhamento e a inclinação das médias móveis para identificar tendências.

        :param ema_periods: Tupla com os períodos das médias móveis, ex: (5, 10, 21).
        :param min_distance: Distância mínima entre as médias móveis para validar a tendência.
        :return:
            - "Uptrend" se as médias estiverem alinhadas em ordem crescente e inclinadas para cima.
            - "Downtrend" se as médias estiverem alinhadas em ordem decrescente e inclinadas para baixo.
            - "No Trend" se nenhum dos critérios for atendido.
        """
        # Calcula as médias móveis para os períodos fornecidos
        ema_values = {period: self.calculate_ema(period) for period in ema_periods}

        # Obtem os últimos valores das médias móveis
        ema_last_values = {period: ema_values[period][-1] for period in ema_periods}
        ema_prev_values = {period: ema_values[period][-2] for period in ema_periods}

        ema5, ema10, ema21 = ema_last_values[5], ema_last_values[10], ema_last_values[21]
        ema5_prev, ema10_prev, ema21_prev = ema_prev_values[5], ema_prev_values[10], ema_prev_values[21]

        # Verificar tendência de alta
        if ema5 > ema10 > ema21:  # Alinhamento crescente
            if ema5 - ema10 > min_distance and ema10 - ema21 > min_distance:  # Distância entre médias
                if ema5 > ema5_prev and ema10 > ema10_prev and ema21 > ema21_prev:  # Inclinação positiva
                    return "Uptrend"

        # Verificar tendência de baixa
        elif ema5 < ema10 < ema21:  # Alinhamento decrescente
            if ema10 - ema5 > min_distance and ema21 - ema10 > min_distance:  # Distância entre médias
                if ema5 < ema5_prev and ema10 < ema10_prev and ema21 < ema21_prev:  # Inclinação negativa
                    return "Downtrend"

        # Caso nenhuma tendência seja detectada
        return "No Trend"




