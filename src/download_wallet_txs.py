"""Download wallet txs history using bscscan or etherscan api
Use cache to avoid api rate limit (cache expires after 3 hours)"""
import os
import requests
import requests_cache

etherscan_api_key = os.environ.get('etherscan_api_key')

requests_cache.install_cache('cache/cache', backend='sqlite', expire_after=60 * 60 * 3)


def get_txs(address: str, endpoint: str = 'etherscan.com', startblock: int = 0) -> list:
    """
    Get normal transactions for a given address
    :param address: Wallet address
    :param endpoint: bscscan.com or etherscan.com
    :param startblock: Number of block to start from
    :return: List of transactions
    """
    url = f"https://api.{endpoint}/api?module=account&action=txlist&address={address}&startblock={startblock}&endblock=99999999&page=1&offset=10000&sort=desc&apikey={etherscan_api_key}"

    response = requests.request("GET", url)

    txs = response.json()
    txs = txs['result']

    if txs is None:
        return []

    return txs


def get_token_txs(address: str, endpoint: str = 'etherscan.com', startblock: int = 0) -> list:
    """
    Get normal transactions for a given address
    :param address: Wallet address
    :param endpoint: bscscan.com or etherscan.com
    :param startblock: Number of block to start from
    :return: List of transactions
    """
    url = f"https://api.{endpoint}/api?module=account&action=tokentx&address={address}&startblock={startblock}&endblock=99999999&page=1&offset=10000&sort=desc&apikey={etherscan_api_key}"

    response = requests.request("GET", url)

    txs = response.json()
    txs = txs['result']

    if txs is None:
        return []

    return txs


def get_internal_txs(address: str, endpoint: str = 'etherscan.com', startblock: int = 0) -> list:
    """
    Get normal transactions for a given address
    :param address: Wallet address
    :param endpoint: bscscan.com or etherscan.com
    :param startblock: Number of block to start from
    :return: List of transactions
    """
    url = f"https://api.{endpoint}/api?module=account&action=txlistinternal&address={address}&startblock={startblock}&endblock=99999999&page=1&offset=10000&sort=desc&apikey={etherscan_api_key}"

    response = requests.request("GET", url)

    txs = response.json()
    txs = txs['result']

    if txs is None:
        return []

    return txs
