import logging

from colorama import init, Fore

# Inicializa o colorama para garantir compatibilidade em todos os sistemas operacionais
init(autoreset=True)


class IQOptionRiskManager:
    def __init__(self, config_file):
        """
        Inicializa o gerenciador de risco com base nas configurações de um arquivo.

        :param config_file: Caminho para o arquivo de configurações
        """
        self.balance, self.max_risk_percentage, self.target_profit_percentage = self.load_config(config_file)
        self.initial_balance = self.balance
        self.max_loss_limit = self.balance * (self.max_risk_percentage / 100)
        self.target_profit_limit = self.balance * (self.target_profit_percentage / 100)
        self.current_profit = 0
        self.current_loss = 0

        # Configuração do logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def load_config(self, config_file):
        """
        Carrega as configurações de risco a partir de um arquivo.

        :param config_file: Caminho para o arquivo de configurações
        :return: Tupla contendo saldo, percentual máximo de risco e percentual alvo de lucro
        """
        config = {}
        try:
            with open(config_file, 'r') as file:
                for line in file:
                    key, value = line.strip().split('=')
                    config[key] = float(value)

            balance = config.get('balance', 1000)
            max_risk_percentage = config.get('max_risk_percentage', 2)
            target_profit_percentage = config.get('target_profit_percentage', 5)

            return balance, max_risk_percentage, target_profit_percentage

        except Exception as e:
            logging.error(f"{Fore.LIGHTRED_EX}Erro ao carregar o arquivo de configuração: {e}")
            return 1000, 2, 5  # Retorna valores padrão em caso de erro

    def can_trade(self, trade_amount):
        """
        Verifica se a operação pode ser realizada com base no gerenciamento de risco.

        :param trade_amount: Quantia da operação
        :return: True se a operação for permitida, False caso contrário
        """

        logging.info(f"{Fore.LIGHTYELLOW_EX}Gerenciador de risco inicializado. Saldo inicial: {self.initial_balance}, "
                     f"Risco máximo por operação: {self.max_risk_percentage}%, "
                     f"Alvo de lucro: {self.target_profit_percentage}%")

        recommended_trade_amount = self.calculate_trade_amount()

        if self.current_loss + trade_amount > self.max_loss_limit:
            logging.warning(f"{Fore.LIGHTYELLOW_EX}Limite de perda atingido. Tentativa de operação de {trade_amount}, "
                            f"perda atual: {self.current_loss}, limite de perda: {self.max_loss_limit}. "
                            f"Valor recomendado: {recommended_trade_amount:.2f}.")
            return False

        if self.current_profit > self.target_profit_limit:
            logging.warning(f"{Fore.LIGHTRED_EX}Alvo de lucro atingido. Lucro atual: {self.current_profit}, "
                            f"limite de lucro: {self.target_profit_limit}. "
                            f"Valor recomendado: {recommended_trade_amount:.2f}.")
            return False

        logging.info(f"{Fore.LIGHTYELLOW_EX}Operação de {trade_amount} permitida. Lucro atual: {self.current_profit}, "
                     f"Perda atual: {self.current_loss}. Valor recomendado: {recommended_trade_amount:.2f}.")
        return True

    def calculate_trade_amount(self):
        """
        Calcula o valor ideal da operação com base no saldo atual e no percentual máximo de risco.
        """
        trade_amount = self.balance * (self.max_risk_percentage / 100)
        return trade_amount

    def update_balance(self, trade_result):
        """
        Atualiza o saldo e as variáveis de controle de risco após cada operação.

        :param trade_result: Resultado da operação (positivo para ganho, negativo para perda)
        """
        self.current_profit += max(0, trade_result)
        self.current_loss += abs(min(0, trade_result))
        self.balance += trade_result
        logging.info(
            f"{Fore.LIGHTMAGENTA_EX}Saldo atualizado: {self.balance:.2f}. Lucro atual: {self.current_profit:.2f}, "
            f"Perda atual: {self.current_loss:.2f}.")

    def reset(self):
        """
        Reseta os valores de controle de lucro e perda.
        """
        self.current_profit = 0
        self.current_loss = 0
        logging.info(f"{Fore.LIGHTWHITE_EX}Gerenciamento de risco resetado.")
