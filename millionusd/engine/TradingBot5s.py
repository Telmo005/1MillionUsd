import datetime
import logging
import os
import time

from colorama import Fore, init

from millionusd.IQOptionClient import IQOptionClient
from millionusd.candles.Candle import Candle
from millionusd.candles.IQOptionDigitalCandleReader import IQOptionDigitalCandleReader
from millionusd.engine.IndicatorAnalyzer import IndicatorAnalyzer

# Inicializa o Colorama para saída colorida no console
init(autoreset=True)

# Configuração do Logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class Config:
    """
    Configurações do bot utilizando variáveis de ambiente para maior flexibilidade.
    """
    EMAIL = os.getenv("IQ_OPTION_EMAIL", "telmo.sigauquejr@gmail.com")
    PASSWORD = os.getenv("IQ_OPTION_PASSWORD", "telmo005")
    ASSET = os.getenv("IQ_OPTION_ASSET", "EURTHB-OTC")
    AMOUNT = float(os.getenv("IQ_OPTION_AMOUNT", 479.79))
    DURATION = int(os.getenv("IQ_OPTION_DURATION", 1))
    INTERVAL = int(os.getenv("IQ_OPTION_INTERVAL", 60))
    CANDLES_TO_ANALYZE = int(os.getenv("CANDLES_TO_ANALYZE", 3))


class TradingBot:
    """
    Bot para executar estratégias de trading na IQ Option.
    """

    def __init__(self, config):
        self.config = config

    def log(self, level, message):
        """Loga mensagens com níveis e cores apropriadas."""
        color_map = {"info": Fore.WHITE, "warning": Fore.YELLOW, "error": Fore.LIGHTRED_EX}
        getattr(logger, level, logger.info)(f"{color_map.get(level, Fore.WHITE)}[BOT] {message}")

    def analyze_ema_direction(self, ema_values):
        """Determina a direção do EMA com base na inclinação."""
        slope_current = ema_values[-2] - ema_values[-3]
        slope_previous = ema_values[-3] - ema_values[-4]

        if slope_current > 0 >= slope_previous:
            return "up"
        elif slope_current < 0 <= slope_previous:
            return "down"
        elif slope_current > 0:
            return "up"
        elif slope_current < 0:
            return "down"
        return "flat"

    def execute_trade(self, iq_client, candle_reader, action, amount, price):
        """Executa uma operação de trading e avalia a próxima ação."""
        iq_client.execute_trade(self.config.ASSET, 1000, 'call', self.config.DURATION)
        time.sleep(6)
        # if action == 'put':
        #     new_action = "call"
        # else:
        #     new_action = "put"

        # candles = candle_reader.get_realtime_candles(self.config.ASSET, self.config.INTERVAL)
        # new_prices = Candle().read(candles)

        # if price["open"][-1] < new_prices["close"][-1]:
        #     if action == 'put':
        #         new_action = "call"
        #
        # else:
        #     if action == 'call':
        #         new_action = "put"

        iq_client.trade(self.config.ASSET, self.config.DURATION, 1085.68, "put")

    def analyze_and_trade(self, iq_client, candle_reader):
        """Analisa candles e executa operações com base em estratégias."""
        try:
            candles = candle_reader.get_realtime_candles(self.config.ASSET, self.config.INTERVAL)
            price = Candle().read(candles)

            ema_values = IndicatorAnalyzer(price["close"]).calculate_ema(price["close"], 2)
            direction = self.analyze_ema_direction(ema_values)

            if direction in ["up", "down"]:
                action = "call" if direction == "up" else "put"

                self.execute_trade(iq_client, candle_reader, action, self.config.AMOUNT, price)
                self.log("info", f"Operação executada: {action.upper()} no ativo {self.config.ASSET}.")
        except Exception as e:
            self.log("error", f"Erro durante análise: {e}")

    def get_next_execution_time(self, iq_client):
        """
        Calcula o próximo horário de execução baseado no timestamp do servidor.
        Retorna o próximo horário de execução.
        """
        # Obtém o timestamp atual do servidor
        server_timestamp = iq_client.connection.get_server_timestamp()  # Ex.: 1737298699.373

        # Separa parte inteira (segundos) e fracionária (milissegundos)
        seconds = int(server_timestamp)
        fractional_part = server_timestamp - seconds

        # Calcula os segundos para o próximo minuto
        current_seconds_in_minute = seconds % 60
        seconds_to_next_minute = 60 - current_seconds_in_minute - fractional_part

        # Calcula o timestamp da próxima execução
        next_execution_timestamp = server_timestamp + seconds_to_next_minute
        next_execution_timestamp += 3
        # Converte o timestamp da próxima execução para o formato de hora
        next_execution_time = datetime.datetime.fromtimestamp(next_execution_timestamp)

        # Exibe a hora da próxima execução no formato desejado
        self.log("info", f"Próxima execução às: {next_execution_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")

        return next_execution_time

    def run(self):
        """Executa o bot de trading."""
        self.log("info", "Inicializando bot...")
        try:
            with IQOptionClient(self.config.EMAIL, self.config.PASSWORD) as iq_client:
                iq_client.update_assets_cache()
                candle_reader = IQOptionDigitalCandleReader(iq_client)
                candle_reader.start_candles_stream(self.config.ASSET, self.config.INTERVAL, 100)

                while True:
                    # Chama o método para obter o próximo horário de execução
                    next_execution_time = self.get_next_execution_time(iq_client)

                    server_timestamp = iq_client.connection.get_server_timestamp()  # Ex.: 1737298699.373

                    # Converte o timestamp do servidor para datetime
                    current_time = datetime.datetime.fromtimestamp(server_timestamp)

                    # Calcula o tempo até a próxima execução (em segundos)
                    time_to_wait = (next_execution_time - current_time).total_seconds()

                    # Aguarda até o próximo minuto exato
                    # time.sleep(time_to_wait)

                    # Executa a análise e operação
                    self.analyze_and_trade(iq_client, candle_reader)

        except Exception as e:
            self.log("error", f"Erro fatal no bot: {e}")

if __name__ == "__main__":
    bot = TradingBot(Config)
    bot.run()
