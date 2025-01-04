import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class AssetAnalyzer:
    def __init__(self, iq_client):
        """
        Inicializa o analisador de ativos.

        :param iq_client: Cliente IQ Option para obter os ativos disponíveis.
        """
        if not iq_client:
            raise ValueError("O cliente IQ Option não pode ser None.")
        self.iq_client = iq_client
        self.assets_cache = None
        self.otc_cache = None

    from typing import List, Set

    def get_digital_assets(self, available_assets, excluded_assets: Set[str]) -> List[str]:
        """
        Retorna a lista de nomes de ativos digitais disponíveis, excluindo os ativos especificados.

        :param available_assets: Lista de ativos disponíveis.
        :param excluded_assets: Conjunto de ativos a serem ignorados.
        :return: Lista de nomes de ativos digitais disponíveis.
        """
        if not isinstance(excluded_assets, set):
            logger.error("excluded_assets deve ser um conjunto (set).")
            raise TypeError("Tipo inválido para excluded_assets.")

        digital_asset_names = [
            asset["name"] for asset in available_assets
            if asset.get("type") == "digital" and asset.get("name") not in excluded_assets
        ]

        logger.info(f"Ativos digitais disponíveis: {digital_asset_names}")
        return digital_asset_names
