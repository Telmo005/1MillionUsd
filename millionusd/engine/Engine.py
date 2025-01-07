import logging
import time
from datetime import datetime

from colorama import Fore, Style, init
from millionusd.IQOptionClient import IQOptionClient
from millionusd.candles.IQOptionDigitalCandleReader import IQOptionDigitalCandleReader
from millionusd.engine import ConfigFileManager
from millionusd.engine.AssetAnalyzer import AssetAnalyzer
from millionusd.engine.CandlerAnalyzer import CandleAnalyzer

# Inicializa o colorama
init(autoreset=True)

# Configurações do logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

excluded_assets = {"USSPX500:N", "USNDAQ100:N", "US30:N", "USDCAD-op", "USDCHF-op"}


def log_info(message):
    """Log de informações com texto em branco."""
    logger.info(f"{Fore.WHITE}{message}")


def log_error(message):
    """Log de erros com texto em vermelho."""
    logger.error(f"{Fore.LIGHTRED_EX}{message}")


def run_engine():
    """Função principal que executa o bot de trading."""
    log_info("Inicializando o bot de trading...")

    config_manager = ConfigFileManager.ConfigFileManager('../../config_files/FileConfig.json')
    config = config_manager.read_config()

    try:
        with IQOptionClient(config.get("email"), config.get("password")) as iq_client:
            log_info("Cliente IQ Option conectado com sucesso.")

            assets_updated = iq_client.update_assets_cache()
            log_info("Cache de ativos atualizado.")

            digital_assets = AssetAnalyzer(iq_client).get_digital_assets(assets_updated, excluded_assets)
            log_info(f"Ativos digitais filtrados: {len(digital_assets)} encontrados.")

            candle_reader_factory = IQOptionDigitalCandleReader(iq_client)

            while True:
                try:
                    log_info("Iniciando análise de candles...")

                    analyzer = CandleAnalyzer(iq_client, candle_reader_factory=candle_reader_factory)
                    interval = 60  # 1 minuto
                    count = 100  # Últimos 100 candles

                    moving_average_patterns = analyzer.get_moving_average_pattern(digital_assets, interval, count)
                    log_info("Padrões de média móvel obtidos com sucesso.")

                    extreme_assets = analyzer.get_asset_with_extreme_candles(moving_average_patterns)
                    asset_with_min = extreme_assets.get("asset_with_min_candles")
                    print(extreme_assets)

                    config['asset'] = asset_with_min
                    vld_best_asset = False
                    config['get_patter_1'] = vld_best_asset
                    config_manager.write_config(config)
                    log_info(f"Ativo atualizado para: {asset_with_min}")

                    while not vld_best_asset:
                        config = config_manager.read_config()
                        vld_best_asset = config.get("get_patter_1")
                        log_info("Esperando o comando para buscar novo ativo...")
                        time.sleep(20)

                except Exception as e:
                    log_error(f"Erro encontrado ao processar candles: {str(e)}. Reiniciando...")
                    continue

    except Exception as e:
        log_error(f"Erro ao inicializar o cliente IQ Option: {str(e)}.")


if __name__ == "__main__":
    run_engine()
