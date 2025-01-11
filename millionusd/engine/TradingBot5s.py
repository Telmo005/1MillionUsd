import logging
import os
from enum import Enum
from typing import List, Tuple
from datetime import datetime
import numpy as np
from colorama import Fore, init
from typing import Any, List

from millionusd.IQOptionClient import IQOptionClient
from millionusd.candles.Candle import Candle
from millionusd.candles.IQOptionDigitalCandleReader import IQOptionDigitalCandleReader
from millionusd.engine.IndicatorAnalyzer import IndicatorAnalyzer

# Inicializa o Colorama
init(autoreset=True)

# Configuração do Logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Carregando configurações do ambiente/config file
config = {
    "email": os.getenv("IQ_OPTION_EMAIL", "telmo.sigauquejr@gmail.com"),
    "password": os.getenv("IQ_OPTION_PASSWORD", "telmo005"),
    "asset": os.getenv("IQ_OPTION_ASSET", "EURTHB-OTC"),
    "amount": int(os.getenv("IQ_OPTION_AMOUNT", 1000)),
    "duration": int(os.getenv("IQ_OPTION_DURATION", 1)),
    "config_path": os.getenv("CONFIG_PATH", "../../config_files/FileConfig.json"),
}

class TradeDirection(Enum):
    """Enum para representar a direção da operação."""
    CALL = "call"
    PUT = "put"
    NONE = "none"

class TradingBot:
    """Classe responsável por identificar curvaturas nas EMAs e executar operações de trading."""

    def __init__(self, config: dict):
        self.config = config
        self.previous_ema = None

    @staticmethod
    def log_info(message: str) -> None:
        logger.info(f"{Fore.WHITE}{message}")

    @staticmethod
    def log_error(message: str) -> None:
        logger.error(f"{Fore.LIGHTRED_EX}{message}")

    def execute_trade(self, iq_client: IQOptionClient, direction: TradeDirection) -> None:
        """Executa uma operação na IQ Option."""
        asset = self.config.get("asset")
        amount = self.config.get("amount")
        duration = self.config.get("duration")

        self.log_info(f"Iniciando operação: {direction.value.upper()} | Ativo: {asset} | Valor: {amount} | Duração: {duration}m")

        try:
            iq_client.trade(asset, duration, amount, direction.value)
            self.log_info(f"Operação '{direction.value.upper()}' executada com sucesso no ativo {asset}.")
        except Exception as e:
            self.log_error(f"Erro ao executar operação '{direction.value.upper()}': {str(e)}")

    @staticmethod
    def detect_curvatures(ema: np.ndarray, times: List[datetime]) -> List[Tuple[str, datetime, float]]:
        """Detecta curvaturas na EMA e retorna uma lista com picos e vales."""
        curvatures = []
        for i in range(1, len(ema) - 1):
            if ema[i - 1] < ema[i] > ema[i + 1]:
                curvatures.append(("Pico", times[i], ema[i]))
            elif ema[i - 1] > ema[i] < ema[i + 1]:
                curvatures.append(("Vale", times[i], ema[i]))
        return curvatures

    def analyze_and_trade(self, iq_client: IQOptionClient, candles: Any) -> None:
        """Analisa os candles para identificar curvaturas nas EMAs e executa operações."""
        self.log_info("Iniciando análise de candles...")

        data = Candle().read(candles)
        close_prices = np.array(data['close'])
        times = data['from']

        analyzer = IndicatorAnalyzer(data)
        ema = analyzer.calculate_ema(close_prices, 10)

        curvatures = self.detect_curvatures(ema, times)

        for curvature_type, time, value in curvatures:

            # Converte o timestamp para datetime
            timestamp_datetime = datetime.fromtimestamp(time)
            # Formata o datetime para o formato desejado
            formatted_time = timestamp_datetime.strftime("%d-%m-%Y %H:%M:%S")


            if curvature_type == "Pico":
                self.log_info(f"{Fore.GREEN}Pico detectado - Hora: {formatted_time}, EMA: {value}")
                self.execute_trade(iq_client, TradeDirection.CALL)
            elif curvature_type == "Vale":
                self.log_info(f"{Fore.RED}Vale detectado - Hora: {formatted_time}, EMA: {value}")
                self.execute_trade(iq_client, TradeDirection.PUT)

        self.previous_ema = ema

    def run(self) -> None:
        """Executa o bot de trading."""
        self.log_info("Inicializando o bot de trading...")

        try:
            with IQOptionClient(self.config.get("email"), self.config.get("password")) as iq_client:
                self.log_info("Cliente IQ Option conectado com sucesso.")

                interval = 5  # Intervalo de tempo para os candles
                candle_reader = IQOptionDigitalCandleReader(iq_client)
                iq_client.update_assets_cache()

                candle_reader.start_candles_stream(self.config.get("asset"), interval, 100)

                while True:
                    try:
                        self.log_info("Obtendo candles em tempo real...")
                        candles = candle_reader.get_realtime_candles(self.config.get("asset"), interval)
                        self.analyze_and_trade(iq_client, candles)
                    except Exception as e:
                        self.log_error(f"Erro ao processar candles: {str(e)}. Reiniciando...")

        except Exception as e:
            self.log_error(f"Erro ao inicializar o cliente IQ Option: {str(e)}.")

if __name__ == "__main__":
    bot = TradingBot(config)
    bot.run()
