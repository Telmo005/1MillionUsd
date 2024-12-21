import logging
import os
import time

from colorama import init, Fore

from millionusd.IQOptionClient import IQOptionClient
from iqoptionapi.stable_api import IQ_Option

from millionusd.candles.IQOptionDigitalCandleReader import IQOptionDigitalCandleReader
from millionusd.indicators.CandleAnalyzer import CandleAnalyzer
from millionusd.riskManager.IQOptionRiskManager import IQOptionRiskManager
from millionusd.trader.IQOptionTrader import IQOptionTrader

# Inicializa o colorama para garantir compatibilidade em todos os sistemas operacionais
init(autoreset=True)

# Configuração do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Credenciais e configurações de operação
email = "telmo.sigauquejr@gmail.com"
password = "telmo005"
asset = "NZDCAD-OTC"
interval = 60  # Intervalo de candles (em minutos)
count = 100  # Quantidade de candles a buscar
trade_amount = 100  # Valor por operação

def run_trading_bot():
    """Executa o bot de trading."""
    with IQOptionClient(email, password) as iq_client:

        available_assets = iq_client.get_available_assets()

        if available_assets:
            print("Ativos disponíveis para negociação:")
            for asset1 in available_assets:
                print(asset1)
        else:
            print("Nenhum ativo disponível no momento.")


        candle_reader = IQOptionDigitalCandleReader(iq_client)

        while True:
            try:
                # Obter candles digitais
                candles = candle_reader.get_digital_candles(asset, interval, count)

                if candles:
                    # Usar o último candle como o candle atual
                    current_candle = candles[-1]

                    # Instanciar o analisador de candles
                    analyzer = CandleAnalyzer(current_candle, candles)

                    ema5 = analyzer.calculate_ema(5)[-1]
                    ema10 = analyzer.calculate_ema(10)[-1]
                    ema21 = analyzer.calculate_ema(21)[-1]

                    # Critérios de compra
                    if ema5 > ema10 > ema21:  # Alinhamento de médias móveis
                        if ema5 - ema10 > 0.1 and ema10 - ema21 > 0.1:  # Distância entre médias
                            if ema5 > ema5 - 1 and ema10 > ema10 - 1 and ema21 > ema21 - 1:  # Inclinação positiva
                                trade_id = trader.place_digital_trade(asset, trade_amount, 'call', 1)

                    # Critérios de venda
                    elif ema5 < ema10 < ema21:  # Alinhamento de médias móveis
                        if ema10 - ema5 > 0.1 and ema21 - ema10 > 0.1:  # Distância entre médias
                            if ema5 < ema5 - 1 and ema10 < ema10 - 1 and ema21 < ema21 - 1:  # Inclinação negativa
                                trade_id = trader.place_digital_trade(asset, trade_amount, 'put', 1)

                    logging.info(f"{Fore.LIGHTWHITE_EX}EMA(5): {ema5:.2f}, EMA(10): {ema10:.2f}, EMA(21): {ema21:.2f}")
                    logging.info(f"{Fore.LIGHTWHITE_EX}Preço de fechamento atual: {current_candle.close_price:.2f}")

                    # Configuração do gerenciador de risco
                    config_file_path = os.path.abspath('riskManager/RiskManagerConfigFile.txt')
                    risk_manager = IQOptionRiskManager(config_file_path)
                    trader = IQOptionTrader(iq_client, risk_manager)

                # Esperar antes de buscar novos candles (tempo deve ser compatível com o intervalo)
                #time.sleep(interval * 60)

            except Exception as e:
                logging.error(f"{Fore.LIGHTRED_EX}Erro encontrado: {str(e)}. Reiniciando a execução...")


if __name__ == "__main__":
    while True:
        run_trading_bot()
