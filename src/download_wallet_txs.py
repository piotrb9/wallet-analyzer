"""Download wallet txs history using bscscan or etherscan api.
Use cache to avoid api rate limit (cache expires after 3 hours)
"""
import os
import time

import requests
import requests_cache

etherscan_api_key = os.environ.get('etherscan_api_key')
helius_api_key = os.environ.get('helius_api_key')

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


class SolanaDataDownloader:
    """
    Download wallet txs history using solana.fm api
    """

    def __init__(self, address: str):
        """
        Create a new DataDownloader object with given address

        :param address: Wallet address
        """
        self.address = address

    def get_txs(self) -> list:
        """
        Get normal transactions for a given address

        :return: List of transactions
        """
        all_txs = []
        page = 1
        url = f"https://api.solana.fm/v0/accounts/{self.address}/transfers?page={page}"
        response = requests.request("GET", url)
        data = response.json()
        total_pages = data['pagination']['totalPages']
        print("Total pages: ", total_pages)

        page += 1
        if data['status'] == 'success':
            all_txs.extend(data['results'])
        else:
            print("Error: ", data['message'])

        while page <= total_pages:
            import time
            time.sleep(2)
            print("Page: ", page)
            url = f"https://api.solana.fm/v0/accounts/{self.address}/transfers?page={page}"
            response = requests.request("GET", url)
            data = response.json()
            if data['status'] == 'success':
                all_txs.extend(data['results'])
            else:
                print("Error: ", data['message'])

            page += 1

        # Save the transactions to a file

        import json
        with open(f'data/{self.address}_txs.json', 'w') as file:
            json.dump({'results': all_txs}, file)
        return all_txs

    def get_txs_helius(self, break_time=30 * 60) -> list:
        """
        Get transactions for a given address using the Helius API
        :return:
        """

        all_txs = []
        transactions = []

        url = f'https://api.helius.xyz/v0/addresses/{self.address}/transactions'

        headers = {
            'Content-Type': 'application/json',
        }

        body = {
            'api-key': helius_api_key,
            'limit': 100
            # 'type': ['TRANSFER', 'SWAP', 'UNKNOWN'],
            # 'source': ['SYSTEM_PROGRAM', 'RAYDIUM', 'JUPITER', 'ORCA', 'PHANTOM']
        }
        response = requests.get(url, headers=headers, params=body)

        if response.status_code == 200:
            transactions = response.json()
            # print(transactions)
            all_txs.extend(transactions)
        else:
            print(f"Error: {response.status_code}, {response.text}")
            return []

        last_tx_signature = transactions[-1]['signature']

        while True:
            print(f"Last tx signature: {last_tx_signature}")
            # time.sleep(1)
            body = {
                'api-key': helius_api_key,
                'before': last_tx_signature,
                'limit': 100
            }
            response = requests.get(url, headers=headers, params=body)

            if response.status_code == 200:
                transactions = response.json()
                all_txs.extend(transactions)

                # Stop if there are less than 10 transactions in the last response
                if len(transactions) < 10:
                    break
            else:
                print(f"Error: {response.status_code}, {response.text}")

            last_tx_timestamp = transactions[-1]['timestamp']
            first_tx_timestamp = transactions[0]['timestamp']

            # If the time between the first and last transaction is less than 2 hours, stop (to prevent API overusage)
            if first_tx_timestamp - last_tx_timestamp < break_time:
                # print(last_tx_timestamp, first_tx_timestamp, last_tx_timestamp - first_tx_timestamp)
                print(f"Less than {break_time} seconds between transactions")
                break

            if len(all_txs) > 4000:
                break

            last_tx_signature = transactions[-1]['signature']

        # Remove duplicates by signature
        all_txs = list({v['signature']: v for v in all_txs}.values())

        return all_txs
