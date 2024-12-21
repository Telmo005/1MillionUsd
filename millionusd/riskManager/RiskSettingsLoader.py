import logging
import os


class RiskSettingsLoader:
    def __init__(self, file_name='RiskManagerConfigFile.txt', config_dir='data'):
        """
        Inicializa o carregador de configurações de risco.
        :param file_name: Nome do arquivo de configuração (padrão: 'RiskManagerConfigFile.txt').
        :param config_dir: Diretório onde o arquivo de configuração está localizado (padrão: 'data').
        """
        # Definir o caminho dinâmico baseado no diretório raiz do projeto
        project_root = os.path.dirname(os.path.abspath(__file__))
        self.file_path = os.path.join(project_root, config_dir, file_name)

        self.max_risk_percentage = 4  # Valor padrão
        self.target_profit_percentage = 5  # Valor padrão
        self.load_settings()

    def load_settings(self):
        """
        Carrega as configurações de risco do arquivo especificado.
        """
        if not os.path.exists(self.file_path):
            logging.warning(f"Arquivo de configuração não encontrado: {self.file_path}. Usando valores padrão.")
            return

        try:
            with open(self.file_path, 'r') as file:
                for line in file:
                    key, value = line.strip().split('=')
                    if key == 'max_risk_percentage':
                        self.max_risk_percentage = float(value)
                    elif key == 'target_profit_percentage':
                        self.target_profit_percentage = float(value)
        except Exception as e:
            logging.error(f"Erro ao carregar configurações de risco do arquivo {self.file_path}: {str(e)}")
            raise
