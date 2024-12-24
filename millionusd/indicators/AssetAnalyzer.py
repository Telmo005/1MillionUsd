import logging
import time
from typing import Optional

import numpy as np
from colorama import Fore

from millionusd.IQOptionClient import IQOptionClient
from millionusd.candles.IQOptionDigitalCandleReader import IQOptionDigitalCandleReader
from millionusd.indicators.CandleAnalyzer import CandleAnalyzer

# Configurações gerais
EMAIL = "telmo.sigauquejr@gmail.com"
PASSWORD = "telmo005"
INTERVAL = 60  # Intervalo de candles (em minutos)
COUNT = 32  # Quantidade de candles a buscar
EXCLUDED_ASSETS = {"USSPX500:N", "USNDAQ100:N", "US30:N", "USDCAD-op", "USDCHF-op"}
BEST_ASSET_FILE = "../../config_files/best_asset.npy"

# Configuração de logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


# Escrevendo no arquivo .npy
def save_best_asset(data):
    np.save(BEST_ASSET_FILE, data)
    print(f"Dados salvos em {BEST_ASSET_FILE} com sucesso!")


# Lendo do arquivo .npy
def load_best_asset(file_path):
    try:
        data = np.load(file_path, allow_pickle=True).item()  # Converte para dicionário
        print(f"Dados carregados de {file_path} com sucesso!")
        return data
    except FileNotFoundError:
        print(f"Arquivo {file_path} não encontrado.")
        return None


def calculate_signals(candles):
    """Calcula sinais de compra e venda com base nas médias móveis."""
    analyzer = CandleAnalyzer(candles[-1], candles)
    ema5 = analyzer.calculate_ema(5)
    ema10 = analyzer.calculate_ema(10)
    ema21 = analyzer.calculate_ema(21)

    buy_signals = sum(
        ema5[i] > ema10[i] > ema21[i] and
        ema5[i] - ema10[i] > 0.1 and ema10[i] - ema21[i] > 0.1
        for i in range(len(candles))
    )
    sell_signals = sum(
        ema5[i] < ema10[i] < ema21[i] and
        ema10[i] - ema5[i] > 0.1 and ema21[i] - ema10[i] > 0.1
        for i in range(len(candles))
    )

    return max(buy_signals, sell_signals)


def analyze_asset_signals(iq_client, asset_name: str) -> int:
    """Calcula o número de sinais de compra/venda para um ativo."""
    candle_reader = IQOptionDigitalCandleReader(iq_client)
    candles = candle_reader.get_digital_candles(asset_name, INTERVAL, COUNT)
    if not candles:
        logging.warning(f"{Fore.RED}Nenhum candle encontrado para o ativo {asset_name}.")
        return 0

    return calculate_signals(candles)


def get_best_asset(iq_client) -> Optional[str]:
    """Identifica o melhor ativo para negociação com base nos sinais gerados."""
    available_assets = iq_client.get_available_assets()
    if not available_assets:
        logging.warning(f"{Fore.RED}Nenhum ativo disponível no momento.")
        return None

    best_asset = None
    best_signal_count = 0

    for asset in available_assets:
        asset_name = asset.get("name")
        asset_type = asset.get("type")

        if asset_type != 'digital' or asset_name in EXCLUDED_ASSETS:
            continue

        signals = analyze_asset_signals(iq_client, asset_name)
        logging.info(f"{Fore.CYAN}Ativo {asset_name} analisado com {signals} sinais.")

        if signals > best_signal_count:
            best_signal_count = signals
            best_asset = asset_name

    if best_asset:
        logging.info(f"{Fore.GREEN}Melhor ativo encontrado: {best_asset} com {best_signal_count} sinais.")
    else:
        logging.warning(f"{Fore.RED}Nenhum ativo atende aos critérios da estratégia.")

    return best_asset


def main():
    """Função principal para execução do script."""
    iq_client = IQOptionClient(EMAIL, PASSWORD)
    try:
        if not iq_client.connect():
            logging.error(f"{Fore.RED}Falha ao conectar à IQ Option.")
            return

        while True:
            best_asset = get_best_asset(iq_client)
            if best_asset:
                logging.info(f"{Fore.GREEN}Pronto para negociar o ativo: {best_asset}")
                save_best_asset(best_asset)
                time.sleep(300)

            else:
                logging.warning(f"{Fore.YELLOW}Nenhum ativo encontrado para negociação no momento.")

    except Exception as e:
        logging.error(f"{Fore.RED}Erro inesperado: {e}")
    finally:
        iq_client.disconnect()


if __name__ == "__main__":
    main()
