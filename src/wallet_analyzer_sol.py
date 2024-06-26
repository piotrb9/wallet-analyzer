import json
import os

import pandas as pd
import yaml

from download_wallet_txs import SolanaDataDownloader


class SolanaWalletAnalyzer:
    def __init__(self, wallet: str):
        self.wallet = wallet
        self.transactions = None
        self.swap_txs_df = None

        # Download the transactions data
        self.data_downloader = SolanaDataDownloader(self.wallet)

        # Load the YAML file with os to make it work in the streamlit cloud
        current_location = os.path.dirname(os.path.realpath(__file__))
        yaml_file = os.path.join(current_location, 'data/contracts.yaml')
        with open(yaml_file, 'r') as file:
            config = yaml.safe_load(file)

        self.stablecoins = config['bsc']['stablecoins']

    def load_transactions(self, file_path, limit=100):
        with open(file_path, 'r') as file:
            data = json.load(file)
        self.transactions = data['results'][:limit]

    def classify_tx(self, transaction, swap_type, swap_eth, traded_token) -> tuple:
        tx_from = None
        tx_to = None
        tx_type = "other"
        value = 0

        token_transfers = transaction.get("tokenTransfers", [])

        if swap_type in ["swap_buy", "swap_sell"]:
            value = swap_eth

            if traded_token[-4:] == "pump":
                tx_type = "pumpfun_swap"
            else:
                tx_type = "swap"

        elif transaction["type"] == "TRANSFER" and len(token_transfers) == 0:
            value = transaction["nativeTransfers"][0]["amount"] / 10 ** 9
            tx_from = transaction["nativeTransfers"][0]["fromUserAccount"]
            tx_to = transaction["nativeTransfers"][0]["toUserAccount"]

            if transaction["nativeTransfers"][0]["toUserAccount"] == self.wallet:
                tx_type = "eth_transfer_in"

            elif transaction["nativeTransfers"][0]["fromUserAccount"] == self.wallet:
                tx_type = "eth_transfer_out"

        elif transaction["type"] == "TRANSFER" and len(token_transfers) == 1 and token_transfers[0]["mint"] in self.stablecoins:
            value = transaction["nativeTransfers"][0]["amount"]
            tx_from = transaction["nativeTransfers"][0]["fromUserAccount"]
            tx_to = transaction["nativeTransfers"][0]["toUserAccount"]

            if token_transfers[0]["toUserAccount"] == self.wallet:
                tx_type = "stablecoins_transfer_in"

            elif token_transfers[0]["fromUserAccount"] == self.wallet:
                tx_type = "stablecoins_transfer_out"

        # TODO add token transfer in/out

        return tx_type, tx_from, tx_to, value

    def get_swap_info(self, transaction) -> tuple:
        # sol_sent = 0
        # sol_received = 0
        # tokens_sent = 0
        # tokens_received = 0
        # swap_type = None
        # tokens_involved = set()
        #
        # for action in txn_data:
        #     if action['action'] == 'pay_tx_fees':
        #         fees_paid = action['amount'] / 1000000000  # Convert fees to SOL
        #
        #     if action['action'] == 'transfer':
        #         # transfer_actions.append(action)
        #         if action['token']:
        #             if action['token'] != "":
        #                 tokens_involved.add(action['token'])
        #
        #         if action['token'] == "So11111111111111111111111111111111111111112":
        #             if action['source'] == self.wallet:
        #                 sol_sent += action['amount'] / 1000000000
        #             elif action['destination'] == self.wallet:
        #                 sol_received += action['amount'] / 1000000000
        #
        #         elif action['token'] != "":
        #             if action['destination'] == self.wallet:
        #                 tokens_received += action['amount']
        #             elif action['source'] == self.wallet:
        #                 tokens_sent += action['amount']
        #
        # if sol_sent > 0 and sol_received == 0:
        #     swap_type = "swap_buy"
        # elif sol_received > 0 and sol_sent == 0:
        #     swap_type = "swap_sell"
        #
        # sol_amount = sol_received - sol_sent
        # token_amount = tokens_received - tokens_sent
        #
        # return swap_type, sol_amount, token_amount, tokens_involved

        # -----------------------------
        token_transfers = transaction.get("tokenTransfers", [])

        swap_type = None
        from_token = None
        to_token = None
        from_token_amount = 0
        to_token_amount = 0
        sol_amount = 0
        token_amount = 0
        traded_token = None

        if len(token_transfers) < 2:
            # print("Transaction does not have at least 2 token transfers")
            return None, 0, 0, None

        # Find the token transfer involving the owner_address
        for transfer in token_transfers:
            if transfer["fromUserAccount"] == self.wallet:
                from_token_amount = transfer["tokenAmount"]
                from_token = transfer["mint"]

            elif transfer["toUserAccount"] == self.wallet:
                to_token_amount = transfer["tokenAmount"]
                to_token = transfer["mint"]

        # Determine if it's a buy or sell based on the transfers
        if from_token == "So11111111111111111111111111111111111111112" and to_token != "So11111111111111111111111111111111111111112" and to_token not in [None, ""]:
            swap_type = "swap_buy"
            sol_amount = from_token_amount
            token_amount = to_token_amount
            traded_token = to_token
        elif to_token == "So11111111111111111111111111111111111111112" and from_token != "So11111111111111111111111111111111111111112" and from_token not in [None, ""]:
            swap_type = "swap_sell"
            sol_amount = to_token_amount
            token_amount = from_token_amount
            traded_token = from_token

        return swap_type, sol_amount, token_amount, traded_token

    def get_data(self):
        # Download the transactions data
        self.transactions = self.data_downloader.get_txs_helius()

        # Load transactions data
        txs_list = []
        # swap_txs_list = []

        for txn in self.transactions:

            swap_type, sol_amount, token_amount, traded_token = self.get_swap_info(txn)
            tx_type, tx_from, tx_to, value = self.classify_tx(txn, swap_type, sol_amount, traded_token)
            price = sol_amount / token_amount if token_amount != 0 else None

            # Fill the txs_list
            txs_list.append({
                "hash": txn['signature'],
                # "blockNumber": txn['blockNumber'],
                "timeStamp": txn['timestamp'],
                "txFee": txn['fee']/10**9,
                "txType": tx_type,
                "from": tx_from,
                "to": tx_to,
                "value": value,
                "swapType": swap_type,
                "swapEth": abs(sol_amount),
                "price": price,
                "tokenValue": abs(token_amount),
                "tokenName": traded_token,
                "tokenSymbol": None,
                "tokenCa": traded_token,
                "tokenDecimal": 12.0,
                "gasPrice": 1,
                "gasUsed": 1,
                "snipe": False,
            })

        self.txs_df = pd.DataFrame(txs_list)
        # self.swap_txs_df = pd.DataFrame(swap_txs_list)
        # return self.swap_txs_df

    def get_swap_txs(self) -> pd.DataFrame:
        """
        Get all the swap transactions (buy and sell) from the txs_df

        """

        swap_txs_df = self.txs_df.loc[
            (self.txs_df['swapType'] == 'swap_buy') | (self.txs_df['swapType'] == 'swap_sell')]

        return swap_txs_df

    def calculate_tokens_txs(self) -> pd.DataFrame:
        """
        Creates self.token_trades df containing aggregated info about trades per every token

        :return: Dataframe with aggregated info about trades per every token and trading metrics per token
        """

        # other swap types means swaps that are not made via known router, but looks like they are trades
        swap_txs_df = self.get_swap_txs()

        # Basic info
        traded_tokens_number = swap_txs_df['tokenCa'].nunique()
        print(f"Traded tokens: {traded_tokens_number}")

        trades_per_token = swap_txs_df.groupby('tokenCa')['tokenName'].count()
        total_trades_number = trades_per_token.sum()

        print(f"Total trades: {total_trades_number}")

        # Buy-sell info per token
        txs_eth = swap_txs_df.groupby(['tokenCa', 'swapType'])['swapEth'].sum()

        txs_tokens = swap_txs_df.groupby(['tokenCa', 'swapType'])['tokenValue'].sum()

        txs_number = swap_txs_df.groupby(['tokenCa', 'swapType'])['hash'].count()

        df = pd.concat([txs_eth, txs_tokens, txs_number], axis=1)
        df.rename(columns={'hash': 'orders'}, inplace=True)

        df['tokenResult'] = df.groupby('tokenCa')['tokenValue'].transform('diff')
        df['ethResult'] = df.groupby('tokenCa')['swapEth'].transform('diff')

        # Calculate % of the unsold tokens
        df['unsoldTokensPercentage'] = -df['tokenResult'] / (df['tokenValue'] + df['tokenResult'].abs()) * 100

        # Calculate percentage trade result per token
        # ethResult/swap buy
        df['tradeResultPercentage'] = df['ethResult'] * 100 / (df['swapEth'] - df['ethResult']) + 100

        return df
