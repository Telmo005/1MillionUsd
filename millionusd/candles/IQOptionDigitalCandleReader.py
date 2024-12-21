import logging
import time
from datetime import datetime

from millionusd.candles.Candle import Candle


class IQOptionDigitalCandleReader:
    def __init__(self, iq_option_client):
        self.iq_option_client = iq_option_client
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(handler)

    def get_digital_candles(self, asset, interval, count):
        """
        Lê os candles digitais mais recentes para o ativo especificado.

        :param asset: O ativo/par de moedas (ex: 'EURUSD')
        :param interval: O intervalo de tempo dos candles em segundos ou minutos
        :param count: Número de candles a serem retornados
        :return: Lista de objetos Candle ou None se houver erro
        """
        try:
            # Usa o timestamp atual para capturar os candles mais recentes
            end_time = int(time.time())

            # Determinar se o intervalo é em minutos ou segundos
            if interval >= 60:
                # Multiplicar apenas se o intervalo for maior que 60 (presumidamente em minutos)
                candles_data = self.iq_option_client.connection.get_candles(asset, interval, count, end_time)
            else:
                # Para intervalos menores, como segundos, não multiplicar por 60
                candles_data = self.iq_option_client.connection.get_candles(asset, interval, count, end_time)

            if not candles_data:
                self.logger.warning("Nenhum dado de candle retornado.")
                return []

            candles = []
            for candle in candles_data:
                start_time = datetime.fromtimestamp(candle['from'])
                end_time = datetime.fromtimestamp(candle['from'] + interval)

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
            self.logger.error(f"Erro ao ler candles digitais: {e}")
            return None

