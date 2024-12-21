class Candle:
    def __init__(self, start_time, end_time, open_price, close_price, high_price, low_price):
        self.start_time = start_time
        self.end_time = end_time
        self.open_price = open_price
        self.close_price = close_price
        self.high_price = high_price
        self.low_price = low_price


class CandlePatternIdentifier:
    def __init__(self, candles):
        self.candles = [
            Candle(
                start_time=candle['start_time'],
                end_time=candle['end_time'],
                open_price=candle['open_price'],
                close_price=candle['close_price'],
                high_price=candle['high_price'],
                low_price=candle['low_price']
            )
            for candle in candles
        ]

    def is_hammer(self, candle):
        body_length = abs(candle.open_price - candle.close_price)
        candle_length = candle.high_price - candle.low_price
        lower_shadow = candle.open_price - candle.low_price if candle.open_price < candle.close_price else candle.close_price - candle.low_price
        return body_length < lower_shadow and body_length < (candle_length / 2)

    def is_inverted_hammer(self, candle):
        body_length = abs(candle.open_price - candle.close_price)
        candle_length = candle.high_price - candle.low_price
        upper_shadow = candle.high_price - max(candle.open_price, candle.close_price)
        return body_length < upper_shadow and body_length < (candle_length / 2)

    def is_bullish_engulfing(self, current_candle, previous_candle):
        return (previous_candle.close_price < previous_candle.open_price and
                current_candle.open_price < current_candle.close_price and
                current_candle.open_price < previous_candle.close_price and
                current_candle.close_price > previous_candle.open_price)

    def is_bearish_engulfing(self, current_candle, previous_candle):
        return (previous_candle.close_price > previous_candle.open_price and
                current_candle.open_price > current_candle.close_price and
                current_candle.open_price > previous_candle.close_price and
                current_candle.close_price < previous_candle.open_price)

    def identify_patterns(self):
        results = []

        for i in range(1, len(self.candles)):
            current_candle = self.candles[i]
            previous_candle = self.candles[i - 1]

            patterns = {
                'start_time': current_candle.start_time,
                'is_hammer': self.is_hammer(current_candle),
                'is_inverted_hammer': self.is_inverted_hammer(current_candle),
                'is_bullish_engulfing': self.is_bullish_engulfing(current_candle, previous_candle),
                'is_bearish_engulfing': self.is_bearish_engulfing(current_candle, previous_candle),
                # Adicione mais padrões conforme necessário
            }

            results.append(patterns)

        return results
