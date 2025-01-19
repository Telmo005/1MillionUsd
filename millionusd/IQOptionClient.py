import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

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

    def subscribe_to_strike_list(self, active, duration):
        """Inscreve o ativo na lista de strikes."""
        try:
            self.connection.subscribe_strike_list(active, duration)
            logging.info(f"[{datetime.now()}] Ativo {active} inscrito para a duração {duration} minutos.")
        except Exception as e:
            logging.error(f"[{datetime.now()}] Erro ao inscrever no strike list para {active}: {e}")

    def unsubscribe_from_strike_list(self, active, duration):
        """Cancela a inscrição do ativo para liberar recursos."""
        try:
            self.connection.unsubscribe_strike_list(active, duration)
            logging.info(f"[{datetime.now()}] Ativo {active} desinscrito com sucesso.")
        except Exception as e:
            logging.error(f"[{datetime.now()}] Erro ao cancelar inscrição do strike list para {active}: {e}")

    def execute_trade(self, active, amount, action, duration):
        """Executa a operação de compra ou venda na IQ Option."""
        try:
            status, operation_id = self.connection.buy_digital_spot(active, amount, action, duration)
            if operation_id == "error":
                logging.error(f"[{datetime.now()}] Erro ao iniciar operação para {active}. Tentando novamente.")
                return None
            logging.info(f"[{datetime.now()}] Operação iniciada com sucesso. ID da operação: {operation_id}.")
            return operation_id
        except Exception as e:
            logging.error(f"[{datetime.now()}] Erro ao executar a operação para {active}: {e}")
            return None

    def monitor_trade(self, operation_id):
        """Monitora o status da operação."""
        while True:
            # Verifica o lucro/perda atual e status da operação
            check, profit = self.connection.check_win_digital_v2(operation_id)
            if check:
                break

        return profit

    def trade(self, active: str, duration: int, amount: float, action: str):
        """
        Realiza uma operação de compra ou venda na IQ Option.

        :param active: Ativo para operar, ex: "EURUSD".
        :param duration: Duração da operação em minutos (1 ou 5).
        :param amount: Valor da operação.
        :param action: "call" para compra ou "put" para venda.
        """
        profit = 0
        try:
            #self.subscribe_to_strike_list(active, duration)

            logging.info(
                f"[{datetime.now()}] Iniciando operação: Ativo={active}, Duração={duration} minutos, Valor={amount}$, "
                f"Ação={action}.")

            operation_id = self.execute_trade(active, amount, action, duration)
            if not operation_id:
                return

            profit = self.monitor_trade(operation_id)

            # Resultado final da operação
            if isinstance(profit, (int, float)):
                result_message = (
                    f"Perda de {abs(profit)}$." if profit < 0 else f"Lucro de {profit}$."
                )
                logging.info(f"[{datetime.now()}] Operação finalizada. Resultado: {result_message}")
            else:
                logging.error(f"[{datetime.now()}] Operação finalizada com um resultado inválido: {profit}")

        except Exception as e:
            logging.exception(f"[{datetime.now()}] Erro ao realizar operação: {e}")
        #finally:
            #self.unsubscribe_from_strike_list(active, duration)

    def multi_monitor(self, *operation_ids):
        """
        Monitora várias operações ao mesmo tempo, passando os IDs como argumentos.

        :param operation_ids: IDs de operações a serem monitoradas.
        :return: Lista com os resultados (lucro/perda) de cada operação.
        """
        results = []
        with ThreadPoolExecutor() as executor:
            # Dispara múltiplas monitorizações para os IDs de operações
            future_to_id = {
                executor.submit(self.monitor_trade, operation_id): operation_id for operation_id in operation_ids
            }
            for future in as_completed(future_to_id):
                operation_id = future_to_id[future]
                try:
                    result = future.result()
                    results.append(result)
                    result_message = (
                        f"Perda de {abs(result)}$." if result < 0 else f"Lucro de {result}$."
                    )
                    logging.info(f"[{datetime.now()}] Resultado para operação {operation_id}: {result_message}")
                except Exception as e:
                    logging.error(f"[{datetime.now()}] Erro ao monitorar operação {operation_id}: {e}")
        return results

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
