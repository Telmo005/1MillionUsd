import logging
import os
import time

from colorama import init, Fore

from millionusd.IQOptionClient import IQOptionClient
from millionusd.candles.IQOptionDigitalCandleReader import IQOptionDigitalCandleReader
from millionusd.indicators.CandleAnalyzer import CandleAnalyzer
from millionusd.riskManager.IQOptionRiskManager import IQOptionRiskManager
from millionusd.trader.IQOptionTrader import IQOptionTrader

# Inicializa o colorama para garantir compatibilidade em todos os sistemas operacionais
init(autoreset=True)

# Configuração do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configurações da conta e do ativo
EMAIL = "telmo.sigauquejr@gmail.com"
PASSWORD = "telmo005"
ASSET = "GBPUSD-OTC"
INTERVAL = 1  # Intervalo de tempo dos candles
COUNT = 200  # Quantidade de candles
TRADE_AMOUNT = 1  # Valor da operação

def setup_risk_manager():
    """Configura o gerenciador de risco."""
    config_file_path = os.path.abspath('riskManager/RiskManagerConfigFile.txt')
    return IQOptionRiskManager(config_file_path)

def detect_trend_and_place_trade(candle_reader, trader):
    """
    Detecta tendência e coloca operações com base nos cruzamentos de médias móveis.
    """
    candles = candle_reader.get_digital_candles(ASSET, INTERVAL, COUNT)

    if candles:
        current_candle = candles[-1]
        analyzer = CandleAnalyzer(current_candle, candles)

        # Calcula as médias móveis
        short_ema = analyzer.calculate_ema(period=12)
        long_ema = analyzer.calculate_ema(period=26)
        adx = analyzer.calculate_adx(period=14)
        trader.place_digital_trade(ASSET, TRADE_AMOUNT, 'call', 1)
        trader.place_digital_trade(ASSET, TRADE_AMOUNT, 'put', 1)


    else:
        logging.warning(f"{Fore.LIGHTYELLOW_EX}Nenhum candle recebido.")

def run_trading_bot():
    """Função principal que executa o bot de trading."""
    with IQOptionClient(EMAIL, PASSWORD) as iq_client:
        candle_reader = IQOptionDigitalCandleReader(iq_client)
        risk_manager = setup_risk_manager()
        trader = IQOptionTrader(iq_client, risk_manager)

        while True:
            try:
                detect_trend_and_place_trade(candle_reader, trader)
                time.sleep(5)  # Aguarda 5 segundos entre verificações

            except Exception as e:
                logging.error(f"{Fore.LIGHTRED_EX}Erro encontrado: {str(e)}. Reiniciando...")
                time.sleep(5)  # Aguarda 5 segundos antes de reiniciar

if __name__ == "__main__":
    run_trading_bot()
