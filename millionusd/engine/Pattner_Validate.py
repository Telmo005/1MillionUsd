import logging
import time
from datetime import datetime
from typing import Any, List, Dict

import numpy as np
import talib
from colorama import Fore, init

from millionusd.IQOptionClient import IQOptionClient
from millionusd.engine.AssetAnalyzer import AssetAnalyzer

# Inicializa o Colorama
init(autoreset=True)

# Configuração do Logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

SLEEP_TIME = 0.001  # Tempo de descanso entre análises

class CandleCurvatureDetector:
    """Classe responsável por detectar curvaturas nos candles e no EMA."""

    def __init__(self, iq_client: IQOptionClient, asset: str, interval: int = 60, ema_period: int = 10):
        self.iq_client = iq_client
        self.asset = asset
        self.interval = interval
        self.ema_period = ema_period
        self.uptrend_count = 0
        self.downtrend_count = 0

    def fetch_closed_candles(self, count: int = 100, end_from_time: int = None) -> List[Dict[str, Any]]:
        """Obtém candles já fechados do ativo especificado."""
        if end_from_time is None:
            end_from_time = int(time.time())

        candles = self.iq_client.connection.get_candles(self.asset, self.interval, count, end_from_time)
        if not candles:
            raise ValueError(f"Nenhum candle encontrado para o ativo {self.asset}.")

        return candles

    def calculate_ema(self, candles: List[Dict[str, Any]]) -> List[float]:
        """Calcula a linha do Exponential Moving Average (EMA)."""
        close_prices = np.array([candle["close"] for candle in candles])
        return talib.EMA(close_prices, timeperiod=self.ema_period)

    def detect_curvatures(self, ema: List[float], times: List[datetime]) -> None:
        """Detecta as curvaturas no EMA."""
        for i in range(1, len(ema) - 1):
            if ema[i - 1] < ema[i] > ema[i + 1]:  # Pico
                self.uptrend_count += 1
                logger.info(f"{Fore.GREEN}Pico detectado - Ativo: {self.asset}, Hora: {times[i]}, EMA: {ema[i]}")
            elif ema[i - 1] > ema[i] < ema[i + 1]:  # Vale
                self.downtrend_count += 1
                logger.info(f"{Fore.RED}Vale detectado - Ativo: {self.asset}, Hora: {times[i]}, EMA: {ema[i]}")

    def analyze(self) -> Dict[str, int]:
        """Executa a análise completa do ativo."""
        candles = self.fetch_closed_candles(count=100)
        times = [datetime.fromtimestamp(candle["from"]).strftime("%Y-%m-%d %H:%M:%S") for candle in candles]
        ema = self.calculate_ema(candles)
        self.detect_curvatures(ema, times)

        logger.info(f"Análise finalizada para {self.asset}: {self.uptrend_count} picos, {self.downtrend_count} vales.")
        return {"picos": self.uptrend_count, "vales": self.downtrend_count}


def analyze_assets(iq_client: IQOptionClient) -> None:
    """Percorre todos os ativos e realiza a análise sequencialmente."""
    assets_updated = iq_client.update_assets_cache()
    excluded_assets = {"USSPX500:N", "USNDAQ100:N", "US30:N", "USDCAD-op", "USDCHF-op"}
    digital_assets = AssetAnalyzer(iq_client).get_digital_assets(assets_updated, excluded_assets)

    logger.info(f"{len(digital_assets)} ativos encontrados. Iniciando análise...")

    results = {}
    for asset in digital_assets:
        try:
            logger.info(f"Iniciando análise para o ativo: {asset}")
            detector = CandleCurvatureDetector(iq_client, asset)
            result = detector.analyze()
            total_changes = result["picos"] + result["vales"]
            results[asset] = total_changes
        except Exception as e:
            logger.error(f"Erro ao analisar o ativo {asset}: {str(e)}")

    if results:
        max_asset = max(results, key=results.get)
        min_asset = min(results, key=results.get)
        logger.info(f"Ativo com MAIS mudanças: {max_asset} ({results[max_asset]} mudanças)")
        logger.info(f"Ativo com MENOS mudanças: {min_asset} ({results[min_asset]} mudanças)")
    else:
        logger.info("Nenhuma mudança detectada nos ativos analisados.")


if __name__ == "__main__":
    config = {
        "email": "telmo.sigauquejr@gmail.com",
        "password": "telmo005",
    }

    logger.info("Inicializando o detector de curvaturas para múltiplos ativos...")
    try:
        with IQOptionClient(config["email"], config["password"]) as iq_client:
            logger.info("Cliente IQ Option conectado com sucesso.")
            analyze_assets(iq_client)
    except Exception as e:
        logger.error(f"Erro ao executar a análise: {str(e)}")
