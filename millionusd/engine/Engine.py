import logging

from colorama import Fore

from millionusd.IQOptionClient import IQOptionClient
from millionusd.engine import ConfigFileManager

# Configurações do logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configurações da conta e do ativo
EMAIL = "telmo.sigauquejr@gmail.com"
PASSWORD = "telmo005"
ASSET = "GBPUSD"
INTERVAL = 1  # Intervalo de tempo dos candles
TRADE_AMOUNT = 1000  # Valor da operação
DURATION = 1


def run_engine():
    """Função principal que executa o bot de trading."""
    # Inicializa o cliente IQ Option

    config_manager = ConfigFileManager.ConfigFileManager('../../config_files/FileConfig.json')
    config = config_manager.read_config()

    try:
        with IQOptionClient(config.get("email"), config.get("password")) as iq_client:
            # candle_reader = IQOptionDigitalCandleReader(iq_client)
            while True:
                try:

                    # Carregar as configurações
                    if config_manager.config_exists():
                        print(config.get("email"))
                    else:
                        config_manager.write_config({"example_key": "example_value"})

                except Exception as e:
                    logger.error(f"{Fore.LIGHTRED_EX}Erro encontrado ao processar candles: {str(e)}. Reiniciando...")
                    continue

    except Exception as e:
        logger.error(f"{Fore.LIGHTRED_EX}Erro ao inicializar o cliente IQ Option: {str(e)}.")


if __name__ == "__main__":
    run_engine()
