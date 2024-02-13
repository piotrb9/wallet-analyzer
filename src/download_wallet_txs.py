"""Download wallet txs history using bscscan or etherscan api.
Use cache to avoid api rate limit (cache expires after 3 hours)
"""
import os
import requests
import requests_cache

etherscan_api_key = os.environ.get('etherscan_api_key')

requests_cache.install_cache('cache/cache', backend='sqlite', expire_after=60 * 60 * 3)


class DataDownloader:
    """
    Download wallet txs history using bscscan or etherscan api
    """
    def __init__(self, address: str, endpoint: str = 'etherscan.com', startblock: int = 0):
        """
        Create a new DataDownloader object with given address, endpoint and startblock

        :param address: Wallet address
        :param endpoint: bscscan.com or etherscan.com
        :param startblock: Number of block to start from
        """
        self.address = address
        self.endpoint = endpoint
        self.startblock = startblock

    def get_txs(self) -> list:
        """
        Get normal transactions for a given address

        :return: List of transactions
        """
        url = f"https://api.{self.endpoint}/api?module=account&action=txlist&address={self.address}&startblock=" \
              f"{self.startblock}&endblock=99999999&page=1&offset=10000&sort=desc&apikey={etherscan_api_key}"

        response = requests.request("GET", url)

        txs = response.json()
        txs = txs['result']

        if txs is None:
            return []

        return txs

    def get_token_txs(self) -> list:
        """
        Get token transactions for a given address

        :return: List of transactions
        """
        url = f"https://api.{self.endpoint}/api?module=account&action=tokentx&address={self.address}&startblock=" \
              f"{self.startblock}&endblock=99999999&page=1&offset=10000&sort=desc&apikey={etherscan_api_key}"

        response = requests.request("GET", url)

        txs = response.json()
        txs = txs['result']

        if txs is None:
            return []

        return txs

    def get_internal_txs(self) -> list:
        """
        Get internal transactions for a given address

        :return: List of transactions
        """
        url = f"https://api.{self.endpoint}/api?module=account&action=txlistinternal&address={self.address}&startblock=" \
              f"{self.startblock}&endblock=99999999&page=1&offset=10000&sort=desc&apikey={etherscan_api_key}"

        response = requests.request("GET", url)

        txs = response.json()
        txs = txs['result']

        if txs is None:
            return []

        return txs
