class Candle:
    def __init__(self, start_time, end_time, open_price, close_price, max_price, min_price, volume):
        self.start_time = start_time
        self.end_time = end_time
        self.open_price = open_price
        self.close_price = close_price
        self.max_price = max_price
        self.min_price = min_price
        self.volume = volume

    def __repr__(self):
        return (f"Início: {self.start_time}, Fim: {self.end_time}, "
                f"Abertura: {self.open_price}, Fechamento: {self.close_price}, "
                f"Máximo: {self.max_price}, Mínimo: {self.min_price}, "
                f"Volume: {self.volume}")
