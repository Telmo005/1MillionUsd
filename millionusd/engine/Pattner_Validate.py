import datetime
import logging
import os
import time
from time import sleep
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


def wait_until_next_minute():
    """
    Aguarda até o próximo minuto completo, otimizando recursos ao invés de loops contínuos.
    """
    now = datetime.datetime.now()
    seconds_until_next_minute = 60 - now.second
    if seconds_until_next_minute > 0:
        sleep(seconds_until_next_minute)
    logger.info("Aguardando início do próximo minuto para executar ações.")


class Config:
    """
    Configurações do bot utilizando variáveis de ambiente, permitindo fácil customização.
    """
    EMAIL = os.getenv("IQ_OPTION_EMAIL", "telmo.sigauquejr@gmail.com")
    PASSWORD = os.getenv("IQ_OPTION_PASSWORD", "telmo005")
    ASSET = os.getenv("IQ_OPTION_ASSET", "EURTHB-OTC")
    AMOUNT = float(os.getenv("IQ_OPTION_AMOUNT", 479.71))
    DURATION = int(os.getenv("IQ_OPTION_DURATION", 1))
    INTERVAL = int(os.getenv("IQ_OPTION_INTERVAL", 60))
    CANDLES_TO_ANALYZE = int(os.getenv("CANDLES_TO_ANALYZE", 3))


def check_pattern(prices, comparator):
    """
    Verifica padrões de candles.
    Args:
        prices (list): Lista de preços.
        comparator (callable): Função de comparação para verificar o padrão.
    Returns:
        bool: Verdadeiro se o padrão for identificado.
    """
    try:
        return comparator(prices)
    except Exception as e:
        logger.error(f"Erro ao verificar padrão: {e}")
        return False


class TradingBot:
    """
    Bot para executar estratégias de trading na IQ Option.
    """

    def __init__(self, config):
        self.config = config

    def log_info(self, message: str):
        """Loga mensagens de informação."""
        logger.info(f"{Fore.WHITE}[INFO] {message}")

    def log_warning(self, message: str):
        """Loga mensagens de aviso."""
        logger.warning(f"{Fore.YELLOW}[WARN] {message}")

    def log_error(self, message: str):
        """Loga mensagens de erro."""
        logger.error(f"{Fore.LIGHTRED_EX}[ERROR] {message}")


    def log(self, level, message):
        """
        Loga mensagens com diferentes níveis.
        Args:
            level (str): Nível do log (info, warning, error).
            message (str): Mensagem a ser logada.
        """
        colors = {"info": Fore.WHITE, "warning": Fore.YELLOW, "error": Fore.LIGHTRED_EX}
        log_func = getattr(logger, level, logger.info)
        log_func(f"{colors.get(level, Fore.WHITE)}[BOT] {message}")

    def analyze_and_trade(self, candles, iq_client):
        """
        Analisa candles e executa operações com base em estratégias.
        """
        self.log("info", "Analisando candles...")
        try:
            inputs = Candle().read(candles)
            close_prices = inputs["close"]
            open_prices = inputs["open"]

            analyzer = IndicatorAnalyzer(close_prices)
            ema_short = analyzer.calculate_ema(close_prices, 2)

            ema_direction = self.analyze_ema_direction(ema_short)

            if ema_direction in ["up", "down"]:
                trade_action = "put" if ema_direction == "up" else "call"
                time.sleep(6)
                iq_client.trade(self.config.ASSET, self.config.DURATION, self.config.AMOUNT, trade_action)
                self.log("info", f"Operação executada: {trade_action.upper()} no ativo {self.config.ASSET}.")
        except Exception as e:
            self.log("error", f"Erro durante análise: {e}")

    def analyze_ema_direction(self, ema_values):
        """
        Determina a direção do EMA.
        """

        # Cálculo da inclinação atual e anterior
        slope_current = ema_values[-2] - ema_values[-3]
        slope_previous = ema_values[-3] - ema_values[-4]

        # Determinar mudanças consistentes na direção
        if slope_current > 0 >= slope_previous:
            self.log_info("EMA mudou direção para cima (reversão de queda para alta).")
            return "none"
        elif slope_current < 0 <= slope_previous:
            self.log_info("EMA mudou direção para baixo (reversão de alta para queda).")
            return "none"
        elif slope_current > 0:
            self.log_info("EMA está subindo (tendência de alta contínua).")
            return "up"
        elif slope_current < 0:
            self.log_info("EMA está descendo (tendência de baixa contínua).")
            return "down"
        else:
            self.log_info("EMA está estável (sem mudanças significativas).")
            return "flat"

    def process_candles(self, candle_reader, iq_client):
        """
        Obtém e processa candles em tempo real.
        """
        try:
            candles = candle_reader.get_realtime_candles(self.config.ASSET, self.config.INTERVAL)
            self.analyze_and_trade(candles, iq_client)
        except Exception as e:
            self.log("error", f"Erro ao processar candles: {e}")

    def run(self):
        """
        Executa o bot de trading.
        """
        self.log("info", "Inicializando bot...")
        try:
            with IQOptionClient(self.config.EMAIL, self.config.PASSWORD) as iq_client:
                self.log("info", "Conectado ao cliente IQ Option.")
                iq_client.update_assets_cache()

                candle_reader = IQOptionDigitalCandleReader(iq_client)
                candle_reader.start_candles_stream(self.config.ASSET, self.config.INTERVAL, 100)

                while True:
                    #wait_until_next_minute()
                    self.process_candles(candle_reader, iq_client)
        except Exception as e:
            self.log("error", f"Erro fatal no bot: {e}")


if __name__ == "__main__":
    bot = TradingBot(Config)
    bot.run()
