import logging
import time

from colorama import init, Fore

# Inicializa o colorama para garantir compatibilidade em todos os sistemas operacionais
init(autoreset=True)


class IQOptionTrader:
    def __init__(self, iq_client, risk_manager):
        self.iq_client = iq_client
        self.risk_manager = risk_manager

        # Configuração do logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def place_digital_trade(self, active, amount, direction, duration):
        """
        Realiza uma operação digital na IQ Option com gerenciamento de risco.
        """
        if not self.risk_manager.can_trade(amount):
            logging.warning(f"{Fore.LIGHTRED_EX}Operação bloqueada devido ao gerenciamento de risco.")
            return None

        logging.info(
            f"{Fore.LIGHTMAGENTA_EX}Iniciando operação DIGITAL {direction.upper()} para o ativo {active} com valor {amount} "
            f"e duração {duration} minuto(s).")
        _, trade_id = self.iq_client.connection.buy_digital_spot(active, amount, direction, duration)

        if trade_id == "error":
            logging.error(f"{Fore.LIGHTRED_EX}Erro ao realizar a operação digital. Tente novamente.")
            raise Exception("Erro ao realizar a operação digital. Tente novamente.")

        logging.info(f"{Fore.LIGHTGREEN_EX}Operação digital iniciada com sucesso. ID da operação: {trade_id}")
        return trade_id

    def place_forex_trade(self, active, amount, direction, leverage):
        """
        Realiza uma operação Forex na IQ Option com gerenciamento de risco.
        """
        if not self.risk_manager.can_trade(amount):
            logging.warning(f"{Fore.LIGHTRED_EX}Operação bloqueada devido ao gerenciamento de risco.")
            return None

        logging.info(
            f"{Fore.LIGHTWHITE_EX}Iniciando operação FOREX {direction.upper()} para o ativo {active} com valor {amount} "
            f"e alavancagem {leverage}.")
        _, trade_id = self.iq_client.connection.buy_forex(active, amount, direction, leverage)

        if trade_id == "error":
            logging.error(f"{Fore.LIGHTRED_EX}Erro ao realizar a operação Forex. Tente novamente.")
            raise Exception("Erro ao realizar a operação Forex. Tente novamente.")

        logging.info(f"{Fore.LIGHTYELLOW_EX}Operação Forex iniciada com sucesso. ID da operação: {trade_id}")
        return trade_id

    def monitor_trade(self, trade_id, trade_type="digital"):
        """
        Monitora a operação e atualiza o gerenciamento de risco com base no resultado.
        """
        logging.info(f"{Fore.LIGHTYELLOW_EX}Monitorando a operação {trade_id}...")

        while True:
            if trade_type == "digital":
                check, result = self.iq_client.connection.check_win_digital_v2(trade_id)
            elif trade_type == "forex":
                check, result = self.iq_client.connection.check_win_forex_v2(trade_id)
            else:
                logging.error(f"{Fore.LIGHTRED_EX}Tipo de operação inválido.")
                raise ValueError("Tipo de operação inválido.")

            if check:
                break
            time.sleep(1)  # Espera um segundo antes de checar novamente

        if result < 0:
            logging.info(f"{Fore.LIGHTRED_EX}Você perdeu: {abs(result)}$")
        else:
            logging.info(f"{Fore.LIGHTGREEN_EX}Você ganhou: {result}$")

        # Atualiza o gerenciador de risco com o resultado da operação
        self.risk_manager.update_balance(result)
        return result
