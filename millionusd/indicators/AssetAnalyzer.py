import logging
import time

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

# Configuração de logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def get_best_asset(iq_client):
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
        if asset_type == 'digital':
            if asset_name in EXCLUDED_ASSETS:
                logging.info(f"{Fore.YELLOW}Ativo {asset_name} excluído da análise.")
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


def analyze_asset_signals(iq_client, asset_name):
    """Calcula o número de sinais de compra e venda para um ativo."""
    candle_reader = IQOptionDigitalCandleReader(iq_client)
    candles = candle_reader.get_digital_candles(asset_name, INTERVAL, COUNT)
    if not candles:
        logging.warning(f"{Fore.RED}Nenhum candle encontrado para o ativo {asset_name}.")
        return 0

    analyzer = CandleAnalyzer(candles[-1], candles)
    buy_signals = sell_signals = 0

    for i in range(len(candles)):
        ema5 = analyzer.calculate_ema(5)[i]
        ema10 = analyzer.calculate_ema(10)[i]
        ema21 = analyzer.calculate_ema(21)[i]

        # Critérios de compra
        if ema5 > ema10 > ema21:  # Alinhamento de médias móveis
            if ema5 - ema10 > 0.1 and ema10 - ema21 > 0.1:  # Distância entre médias
                if ema5 > ema5 - 1 and ema10 > ema10 - 1 and ema21 > ema21 - 1:  # Inclinação positiva
                    buy_signals += 1

        # Critérios de venda
        elif ema5 < ema10 < ema21:  # Alinhamento de médias móveis
            if ema10 - ema5 > 0.1 and ema21 - ema10 > 0.1:  # Distância entre médias
                if ema5 < ema5 - 1 and ema10 < ema10 - 1 and ema21 < ema21 - 1:  # Inclinação negativa
                    sell_signals += 1

    logging.debug(f"{Fore.MAGENTA}Sinais para {asset_name} - Compras: {buy_signals}, Vendas: {sell_signals}")
    return max(buy_signals, sell_signals)


def main():
    """
    Função principal para execução do script.
    """
    iq_client = IQOptionClient(EMAIL, PASSWORD)
    try:
        if not iq_client.connect():
            logging.error(f"{Fore.RED}Falha ao conectar à IQ Option.")
            return

        while True:
            best_asset = get_best_asset(iq_client)
            if best_asset:
                logging.info(f"{Fore.GREEN}Pronto para negociar o ativo: {best_asset}")
                time.sleep(300)
            else:
                logging.warning(f"{Fore.YELLOW}Nenhum ativo encontrado para negociação no momento.")

    except Exception as e:
        logging.error(f"{Fore.RED}Erro inesperado: {e}")
    finally:
        iq_client.disconnect()


if __name__ == "__main__":
    main()
