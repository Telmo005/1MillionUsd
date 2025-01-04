import logging
from typing import List, Optional, Callable
from datetime import datetime

from millionusd.candles.IQOptionDigitalCandleReader import IQOptionDigitalCandleReader
from millionusd.engine.IndicatorAnalyzer import IndicatorAnalyzer

# Configuração do logging para incluir data, hora, nível do log e a mensagem
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


class CandleAnalyzer:
    def __init__(self, iq_client, candle_reader_factory: Optional[Callable] = None):
        """
        Inicializa o analisador de candles.

        :param iq_client: Cliente IQ Option.
        :param candle_reader_factory: Função de fábrica para criar o leitor de candles.
        :raises ValueError: Se o cliente IQ Option for None.
        """
        if not iq_client:
            self.logger = logging.getLogger(__name__)
            self.logger.error(
                f"{datetime.now()} - Erro ao inicializar o cliente IQ Option: O cliente não pode ser None.")
            raise ValueError("O cliente IQ Option não pode ser None.")

        self.iq_client = iq_client
        self.logger = logging.getLogger(__name__)
        self.candle_reader_factory = candle_reader_factory or (lambda client: IQOptionDigitalCandleReader(client))

    def get_moving_average_pattern(self, assets: List[str], interval: int, count: int) -> dict:
        """
        Recupera candles para uma lista de ativos e analisa padrões de médias móveis.

        :param assets: Lista de nomes de ativos para análise.
        :param interval: Intervalo de tempo em segundos para os candles.
        :param count: Quantidade de candles a recuperar.
        :return: Um dicionário com padrões de candles por ativo.
        """
        if not assets:
            self.logger.warning(f"{datetime.now()} - A lista de ativos está vazia. Nenhuma análise será feita.")
            return {}

        result = {}

        self.logger.info(f"{datetime.now()} - Iniciando o processamento dos candles para cada ativo...")

        for asset in assets:
            try:
                self.logger.debug(f"{datetime.now()} - Tentando recuperar candles para o ativo {asset}...")

                candles = self.candle_reader_factory.get_digital_candles(asset, interval, count)
                self.logger.debug(f"{datetime.now()} - {len(candles)} candles recuperados para {asset}")

                # Realiza a análise (exemplo: padrão de médias móveis)
                indicator_analyzer = IndicatorAnalyzer(candles)
                trend, candles_after_cross = indicator_analyzer.identify_moving_average_convergence()

                # Armazena o padrão (tendência) e a quantidade de candles após o cruzamento
                if trend:
                    result[asset] = {
                        "trend": trend,
                        "candles_after_cross": candles_after_cross
                    }
                    self.logger.info(
                        f"{datetime.now()} - Padrão identificado para {asset}. Tendência: {trend}. Candles após cruzamento: {candles_after_cross}")

            except Exception as e:
                self.logger.error(f"{datetime.now()} - Erro ao processar o ativo {asset}: {str(e)}", exc_info=True)

        self.logger.info(f"{datetime.now()} - Processamento concluído com sucesso.")

        return result

    def get_asset_with_extreme_candles(self, moving_average_patterns: dict) -> dict:
        """
        Identifica o ativo com o maior e o menor número de candles após o cruzamento,
        considerando que o mínimo de candles após o cruzamento seja 1.
        Além disso, determina se a tendência dos ativos com o maior e menor número de candles é alta ou baixa.

        :param moving_average_patterns: Dicionário com os resultados da análise das médias móveis
        :return: Dicionário com os ativos com o maior e o menor número de candles após o cruzamento
        """
        if not moving_average_patterns:
            self.logger.warning(f"{datetime.now()} - Não há padrões de médias móveis encontrados.")
            return {}

        # Inicializa variáveis para armazenar o ativo com maior e menor número de candles
        max_candles = -1
        min_candles = float('inf')
        asset_with_max_candles = None
        asset_with_min_candles = None
        trend_max = None
        trend_min = None

        self.logger.info(
            f"{datetime.now()} - Iniciando a análise dos ativos com maior e menor número de candles após cruzamento...")

        for asset, data in moving_average_patterns.items():
            candles_after_cross = data.get("candles_after_cross", 0)

            # Ignora ativos com candles_after_cross igual a 0
            if candles_after_cross < 3:
                self.logger.debug(
                    f"{datetime.now()} - Ignorando o ativo {asset} com {candles_after_cross} candles após o cruzamento.")
                continue

            trend = data.get("trend", None)

            # Verifica se o ativo tem o maior número de candles
            if candles_after_cross > max_candles:
                max_candles = candles_after_cross
                asset_with_max_candles = asset
                trend_max = trend
                self.logger.debug(
                    f"{datetime.now()} - Atualizado: Ativo com maior número de candles após cruzamento é {asset_with_max_candles} com {max_candles} candles.")

            # Verifica se o ativo tem o menor número de candles
            if candles_after_cross < min_candles:
                min_candles = candles_after_cross
                asset_with_min_candles = asset
                trend_min = trend
                self.logger.debug(
                    f"{datetime.now()} - Atualizado: Ativo com menor número de candles após cruzamento é {asset_with_min_candles} com {min_candles} candles.")

        # Retorna os ativos com maior e menor número de candles após o cruzamento, incluindo a tendência
        if asset_with_max_candles is None or asset_with_min_candles is None:
            self.logger.warning(f"{datetime.now()} - Não há ativos com candles_after_cross maior que 0.")
            return {}

        self.logger.info(
            f"{datetime.now()} - Análise concluída. Ativo com maior número de candles: {asset_with_max_candles}, tendência: {trend_max}.")
        self.logger.info(
            f"{datetime.now()} - Ativo com menor número de candles: {asset_with_min_candles}, tendência: {trend_min}.")

        return {
            "asset_with_max_candles": asset_with_max_candles,
            "max_candles": max_candles,
            "trend_max": trend_max,  # Inclui a tendência do ativo com o maior número de candles
            "asset_with_min_candles": asset_with_min_candles,
            "min_candles": min_candles,
            "trend_min": trend_min  # Inclui a tendência do ativo com o menor número de candles
        }
