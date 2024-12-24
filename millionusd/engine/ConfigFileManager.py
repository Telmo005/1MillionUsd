import json
from pathlib import Path


class ConfigFileManager:
    """
    Uma classe reutilizável para gerenciar arquivos de configuração JSON.
    """

    def __init__(self, file_path: str):
        """
        Inicializa o ConfigFileManager com o caminho para um arquivo JSON.

        :param file_path: Caminho para o arquivo de configuração JSON.
        """
        self.file_path = Path(file_path)

    def read_config(self) -> dict:
        """
        Lê o arquivo JSON e retorna seu conteúdo como um dicionário.

        :return: Dicionário contendo o conteúdo do arquivo JSON.
        :raises FileNotFoundError: Se o arquivo JSON não existir.
        :raises json.JSONDecodeError: Se o arquivo JSON for inválido.
        """
        if not self.file_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {self.file_path}")

        with self.file_path.open('r', encoding='utf-8') as file:
            return json.load(file)

    def write_config(self, data: dict):
        """
        Escreve um dicionário no arquivo JSON, sobrescrevendo seu conteúdo.

        :param data: Dicionário a ser escrito no arquivo JSON.
        """
        with self.file_path.open('w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

    def update_config(self, updates: dict):
        """
        Atualiza o arquivo JSON com os valores fornecidos no dicionário.

        :param updates: Dicionário contendo as atualizações a serem aplicadas.
        """
        try:
            config = self.read_config()
        except FileNotFoundError:
            config = {}

        config.update(updates)
        self.write_config(config)

    def config_exists(self) -> bool:
        """
        Verifica se o arquivo de configuração JSON existe.

        :return: True se o arquivo existir, False caso contrário.
        """
        return self.file_path.exists()

# Exemplo de uso:
# config_manager = ConfigFileManager('config.json')
# if config_manager.config_exists():
#     config = config_manager.read_config()
#     print(config)
# else:
#     config_manager.write_config({"example_key": "example_value"})
# config_manager.update_config({"new_key": "new_value"})
