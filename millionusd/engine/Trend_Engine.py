import logging

from colorama import Fore, init

from millionusd.IQOptionClient import IQOptionClient
from millionusd.candles.IQOptionDigitalCandleReader import IQOptionDigitalCandleReader
from millionusd.engine import ConfigFileManager

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


def run_trnd_engine():
    """Função principal que executa o bot de trading."""
    log_info("Inicializando o bot de trading...")

    config_manager = ConfigFileManager.ConfigFileManager('../../config_files/FileConfig.json')
    config = config_manager.read_config()

    try:
        with IQOptionClient(config.get("email"), config.get("password")) as iq_client:
            log_info("Cliente IQ Option conectado com sucesso.")

            interval = 60  # 1 minuto
            count = 100  # Últimos 100 candles

            candle_reader_factory = IQOptionDigitalCandleReader(iq_client)
            iq_client.update_assets_cache()
            candle_reader_factory.start_candles_stream(config.get("asset"), interval, 100)
            candles = candle_reader_factory.get_realtime_candles(config.get("asset"), interval)

            while True:
                try:
                    print("sucesso ", candles)
                    break
                except Exception as e:
                    log_error(f"Erro encontrado ao processar candles: {str(e)}. Reiniciando...")
                    continue

    except Exception as e:
        log_error(f"Erro ao inicializar o cliente IQ Option: {str(e)}.")


if __name__ == "__main__":
    run_trnd_engine()
