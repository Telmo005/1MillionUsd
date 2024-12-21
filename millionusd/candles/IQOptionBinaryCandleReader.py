import logging
import time
from datetime import datetime

from millionusd.candles.Candle import Candle


class IQOptionBinaryCandleReader:
    def __init__(self, iq_option_client):
        self.iq_option_client = iq_option_client
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(handler)

    def get_binary_candles(self, asset, interval, count):
        """
        Lê os candles para opções binárias de um ativo especificado.

        :param asset: O ativo/par de moedas (ex: 'EURUSD')
        :param interval: O intervalo de tempo dos candles em minutos (ex: 1 para 1 minuto, 5 para 5 minutos)
        :param count: Número de candles a serem retornados
        :return: Lista de candles ou None se houver erro
        """
        try:
            # Usa o timestamp atual para capturar os candles mais recentes
            end_time = int(time.time())
            candles_data = self.iq_option_client.connection.get_candles(asset, interval * 60, count, end_time)

            if not candles_data:
                self.logger.warning("Nenhum dado de candle retornado.")
                return []

            candles = []
            for candle in candles_data:
                    start_time = datetime.fromtimestamp(candle['from'])
                    end_time = datetime.fromtimestamp(candle['from'] + (interval * 60))

                    candle_obj = Candle(
                        start_time=start_time,
                        end_time=end_time,
                        open_price=candle['open'],
                        close_price=candle['close'],
                        max_price=candle['max'],
                        min_price=candle['min'],
                        volume=candle['volume']
                    )

                    candles.append(candle_obj)

            return candles
        except Exception as e:
            self.logger.error(f"Erro ao ler candles binários: {e}")
            return None
