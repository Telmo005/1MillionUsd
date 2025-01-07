import logging
from enum import Enum
from typing import Any

import numpy as np
from colorama import Fore, init

from millionusd.IQOptionClient import IQOptionClient
from millionusd.candles.Candle import Candle
from millionusd.candles.IQOptionDigitalCandleReader import IQOptionDigitalCandleReader
from millionusd.engine import ConfigFileManager
from millionusd.engine.IndicatorAnalyzer import IndicatorAnalyzer

# Inicializa o Colorama
init(autoreset=True)

# Configuração do Logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class TradeDirection(Enum):
    """Enum para representar a direção de tendência."""
    CALL = "call"
    PUT = "put"
    NONE = "none"


class TradingBot:
    """Classe responsável por executar o bot de trading."""

    def __init__(self, config_path: str):
        self.config_manager = ConfigFileManager.ConfigFileManager(config_path)
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """Carrega as configurações do arquivo."""
        self.log_info("Carregando configurações do arquivo de configuração...")
        config = self.config_manager.read_config()
        self.log_info("Configurações carregadas com sucesso.")
        return config

    def log_info(self, message: str) -> None:
        """Log de informações com texto em branco."""
        logger.info(f"{Fore.WHITE}{message}")

    def log_error(self, message: str) -> None:
        """Log de erros com texto em vermelho."""
        logger.error(f"{Fore.LIGHTRED_EX}{message}")

    def execute_trade(self, iq_client: IQOptionClient, direction: TradeDirection) -> None:
        """Executa uma operação na IQ Option."""
        asset = self.config.get("asset")
        amount = self.config.get("amount", 1000)
        duration = self.config.get("duration", 1)

        self.log_info(f"Iniciando trade: {direction.value.upper()} | Ativo: {asset} | Valor: {amount} | Duração: {duration}m")
        iq_client.trade(asset, duration, amount, direction.value)
        self.log_info(f"Trade '{direction.value.upper()}' executado com sucesso para o ativo {asset}.")

    def valid_trend_direction(self, ema_short: float, ema_mid: float, ema_long: float) -> TradeDirection:
        """Valida a direção da tendência."""
        self.log_info(f"Validando direção da tendência | EMA Curta: {ema_short} | EMA Média: {ema_mid} | EMA Longa: {ema_long}")
        if ema_short > ema_mid > ema_long:
            self.log_info("Tendência de alta detectada.")
            return TradeDirection.CALL
        elif ema_short < ema_mid < ema_long:
            self.log_info("Tendência de baixa detectada.")
            return TradeDirection.PUT
        self.log_info("Nenhuma tendência válida detectada.")
        return TradeDirection.NONE

    def is_candle_touching_ema(self, open_price: float, close_price: float, ema: float) -> bool:
        """Verifica se o candle anterior toca a linha do EMA."""
        result = open_price < ema < close_price
        self.log_info(f"Verificando se o candle toca a EMA | Open: {open_price} | Close: {close_price} | EMA: {ema} | Toca: {result}")
        return result

    def analyze_and_trade(self, iq_client: IQOptionClient, candles: Any) -> None:
        """Analisa os candles e executa operações com base nos critérios de trading."""
        self.log_info("Iniciando análise de candles...")
        data = Candle().read(candles)
        close_prices = np.array(data['close'])

        analyzer = IndicatorAnalyzer(data)
        ema_short = analyzer.calculate_ema(close_prices, 5)[-1]
        ema_mid = analyzer.calculate_ema(close_prices, 10)[-1]
        ema_long = analyzer.calculate_ema(close_prices, 21)[-1]

        # EMA do candle anterior
        ema_mid_prev = analyzer.calculate_ema(close_prices, 10)[-2]
        ema_long_prev = analyzer.calculate_ema(close_prices, 21)[-2]

        open_prev = data['open'][-2]
        close_prev = data['close'][-2]

        self.log_info(f"Valores EMA calculados | EMA5: {ema_short} | EMA10: {ema_mid} | EMA21: {ema_long}")
        self.log_info(f"Valores do candle anterior | Open: {open_prev} | Close: {close_prev} | EMA10 Prev: {ema_mid_prev} | EMA21 Prev: {ema_long_prev}")

        # Verifica se o candle anterior toca o EMA de 10 ou de 21
        if not self.is_candle_touching_ema(open_prev, close_prev, ema_long_prev) and \
           not self.is_candle_touching_ema(open_prev, close_prev, ema_mid_prev):
            self.log_info("Nenhum toque nos EMAs detectado. Verificando tendência...")
            direction = self.valid_trend_direction(ema_short, ema_mid, ema_long)
            if direction != TradeDirection.NONE:
                self.execute_trade(iq_client, direction)
        else:
            self.log_info("Candle anterior tocou uma das linhas EMA. Nenhuma ação será tomada.")
            #self.config_manager.write_config("valid_trend", False)

    def run(self) -> None:
        """Executa o bot de trading."""
        self.log_info("Inicializando o bot de trading...")
        try:
            with IQOptionClient(self.config.get("email"), self.config.get("password")) as iq_client:
                self.log_info("Cliente IQ Option conectado com sucesso.")

                interval = 60  # 1 minuto
                candle_reader_factory = IQOptionDigitalCandleReader(iq_client)
                iq_client.update_assets_cache()
                candle_reader_factory.start_candles_stream(self.config.get("asset"), interval, 100)

                while True:
                    try:
                        self.log_info("Obtendo candles em tempo real...")
                        candles = candle_reader_factory.get_realtime_candles(self.config.get("asset"), interval)
                        self.config = self._load_config()
                        self.analyze_and_trade(iq_client, candles)
                    except Exception as e:
                        self.log_error(f"Erro ao processar candles: {str(e)}. Reiniciando...")
        except Exception as e:
            self.log_error(f"Erro ao inicializar o cliente IQ Option: {str(e)}.")


if __name__ == "__main__":
    bot = TradingBot(config_path="../../config_files/FileConfig.json")
    bot.run()
