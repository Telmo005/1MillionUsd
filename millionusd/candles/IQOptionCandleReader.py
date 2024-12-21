from datetime import datetime


class IQOptionCandleReader:
    def __init__(self, iq_option_client):
        self.iq_option_client = iq_option_client

    def get_candles(self, asset, interval, count, end_time):
        """
        Lê os candles para o par de moedas especificado em um determinado intervalo.

        :param asset: O par de moedas (ex: 'EURUSD')
        :param interval: O intervalo de tempo dos candles (ex: 1 para 1 minuto, 5 para 5 minutos)
        :param count: Número de candles a serem retornados
        :param end_time: Timestamp final para os candles
        :return: Lista de candles ou None se houver erro
        """
        try:
            print(f"Lendo {count} candles do par {asset} no intervalo de {interval} minutos até {end_time}...")
            candles = self.iq_option_client.connection.get_candles(asset, interval * 60, count, end_time)

            for candle in candles:
                # Tempo de início do candle
                start_time = datetime.utcfromtimestamp(candle['from']).strftime('%Y-%m-%d %H:%M:%S')
                # Tempo de fim do candle (somando o intervalo em segundos ao início)
                end_time = datetime.utcfromtimestamp(candle['from'] + (interval * 60)).strftime('%Y-%m-%d %H:%M:%S')

                print(
                    f"Inicio: {start_time}, Fim: {end_time}, Open: {candle['open']}, Close: {candle['close']}, "
                    f"Max: {candle['max']}, Min: {candle['min']}")

            return candles
        except Exception as e:
            print(f"Erro ao ler candles: {e}")
            return None
