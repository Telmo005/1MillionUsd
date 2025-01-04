import logging

from colorama import init, Fore
from iqoptionapi.stable_api import IQ_Option

# Inicializa o colorama para saída colorida no console
init(autoreset=True)


class IQOptionClient:
    def __init__(self, email: str, password: str):
        """
        Inicializa o cliente IQ Option com as credenciais fornecidas.
        :param email: Email da conta IQ Option.
        :param password: Senha da conta IQ Option.
        """
        self.email = email
        self.password = password
        self.connection = None
        self.assets_cache = None  # Cache para armazenar ativos disponíveis
        self.otc_cache = None  # Cache para armazenar ativos OTC

        # Configuração inicial do logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        logging.info(f"{Fore.LIGHTWHITE_EX}Cliente IQ Option inicializado.")

    def connect(self) -> bool:
        """
        Conecta-se à API do IQ Option.
        :return: True se a conexão for bem-sucedida, False caso contrário.
        """
        try:
            logging.info(f"{Fore.LIGHTWHITE_EX}Conectando à IQ Option...")
            self.connection = IQ_Option(self.email, self.password)
            status, reason = self.connection.connect()
            if not status:
                logging.error(f"{Fore.LIGHTRED_EX}Erro ao conectar: {reason}")
                return False
            logging.info(f"{Fore.LIGHTGREEN_EX}Conexão estabelecida com sucesso!")
            return True
        except Exception as e:
            logging.exception(f"{Fore.LIGHTRED_EX}Erro durante a conexão: {e}")
            return False

    def disconnect(self):
        """
        Desconecta-se da API do IQ Option.
        """
        if self.connection:
            try:
                logging.info(f"{Fore.LIGHTWHITE_EX}Encerrando a sessão...")
                # Fechar conexão manualmente (se necessário, dependendo da implementação da biblioteca)
                self.connection.api.close()
                self.connection = None
                logging.info(f"{Fore.LIGHTGREEN_EX}Sessão encerrada com sucesso.")
            except AttributeError:
                logging.warning(f"{Fore.LIGHTYELLOW_EX}A API não suporta logout explícito. Apenas desconectando.")
                self.connection = None
            except Exception as e:
                logging.exception(f"{Fore.LIGHTRED_EX}Erro ao encerrar a sessão: {e}")
        else:
            logging.warning(f"{Fore.LIGHTYELLOW_EX}Nenhuma conexão ativa para encerrar.")

    def get_balance(self) -> float:
        """
        Obtém o saldo atual da conta conectada.
        :return: Saldo atual ou None em caso de falha.
        """
        if self.connection:
            try:
                return self.connection.get_balance()
            except Exception as e:
                logging.exception(f"{Fore.LIGHTRED_EX}Erro ao obter saldo: {e}")
        else:
            logging.warning(f"{Fore.LIGHTYELLOW_EX}Conexão não ativa.")
        return None

    def update_assets_cache(self):
        """
        Atualiza o cache de ativos disponíveis e OTC.
        """
        try:
            logging.info(f"{Fore.LIGHTWHITE_EX}Atualizando cache de ativos disponíveis...")
            self.connection.update_ACTIVES_OPCODE()
            all_assets = self.connection.get_all_open_time()

            self.assets_cache = [
                {"name": name, "type": asset_type}
                for asset_type, assets in all_assets.items()
                for name, details in assets.items()
                if details.get("open")
            ]
            self.otc_cache = [asset for asset in self.assets_cache if "OTC" in asset["name"]]

            logging.info(f"{Fore.LIGHTGREEN_EX}Cache atualizado com sucesso: {len(self.assets_cache)} ativos.")
            return self.assets_cache
        except Exception as e:
            logging.exception(f"{Fore.LIGHTRED_EX}Erro ao atualizar cache de ativos: {e}")
            self.assets_cache = []
            self.otc_cache = []

    def trade(self, active: str, duration: int, amount: float, action: str):
        """
        Realiza uma operação de compra ou venda na IQ Option.
        :param active: Ativo para operar, ex: "EURUSD".
        :param duration: Duração da operação em minutos (1 ou 5).
        :param amount: Valor da operação.
        :param action: "call" para compra ou "put" para venda.
        """
        try:
            logging.info(
                f"{Fore.LIGHTWHITE_EX}Iniciando operação: Ativo={active}, Duração={duration}, Valor={amount}, Ação={action}.")
            status, operation_id = self.connection.buy_digital_spot(active, amount, action, duration)
            if operation_id == "error":
                logging.error(f"{Fore.LIGHTRED_EX}Erro ao iniciar operação. Por favor, tente novamente.")
                return

            while True:
                check, profit = self.connection.check_win_digital_v2(operation_id)
                if check:
                    break

            if profit < 0:
                logging.warning(f"{Fore.LIGHTYELLOW_EX}Operação finalizada. Resultado: Perda de {abs(profit)}$.")
            else:
                logging.info(f"{Fore.LIGHTGREEN_EX}Operação finalizada. Resultado: Lucro de {profit}$.")
        except Exception as e:
            logging.exception(f"{Fore.LIGHTRED_EX}Erro ao realizar operação: {e}")

    def __enter__(self):
        """
        Permite o uso da classe com o gerenciador de contexto (with).
        """
        if self.connect():
            return self
        raise ConnectionError(f"{Fore.LIGHTRED_EX}Falha ao conectar ao IQ Option.")

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Garante a desconexão ao sair do contexto.
        """
        self.disconnect()
