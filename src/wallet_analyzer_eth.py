"""Analysis of a ETH wallet"""
from download_wallet_txs import get_txs, get_token_txs, get_internal_txs
import pandas as pd
import numpy as np


class WalletAnalyzer:
    def __init__(self, wallet: str, chain='eth') -> None:
        """
        Analyzes wallet transactions
        :param wallet: wallet address
        """
        self.wallet = wallet.lower()
        self.chain = chain

        self.txs_df = None
        self.token_txs_df = None
        self.internal_txs_df = None

        if self.chain == 'eth':
            uniswap_universal_router_address = '0x3fC91A3afd70395Cd496C647d5a6CC9D4B2b7FAD'.lower()
            uniswap_v2_router_2_address = '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D'.lower()
            uniswap_v3_router_2_address = '0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45'.lower()

            self.routers = [uniswap_v2_router_2_address, uniswap_v3_router_2_address, uniswap_universal_router_address]

        # For the implementation of the BSC chain
        elif self.chain == 'bsc':
            pancakeswap_v2_universal_router = '0x10ED43C718714eb63d5aA57B78B54704E256024E'.lower()
            pancakeswap_v3_universal_router = '0x13f4EA83D0bd40E75C8222255bc855a974568Dd4'.lower()

            self.routers = [pancakeswap_v2_universal_router, pancakeswap_v3_universal_router]

    def get_data(self, startblock=0):
        """
        Download all the data (transactions, internal transactions, token transactions)
        Change the dtypes
        Decode Universal router input
        :param startblock: block number to start from
        :return:
        """
        api_endpoint = 'etherscan.io' if self.chain == 'eth' else 'bscscan.com'

        txs_list = get_txs(self.wallet, api_endpoint, startblock=startblock)
        print(f"Downloaded total: {len(txs_list)} transactions")

        # Create a dataframe
        txs_df = pd.DataFrame(txs_list)

        if txs_df.shape[0] != 0:
            txs_df['blockNumber'] = txs_df['blockNumber'].astype(int)
            txs_df['timeStamp'] = txs_df['timeStamp'].astype(int)
            txs_df['nonce'] = txs_df['nonce'].astype(int)
            txs_df['transactionIndex'] = txs_df['transactionIndex'].astype(int)
            txs_df['value'] = txs_df['value'].astype(
                float) / 10 ** 18
            txs_df['gas'] = txs_df['gas'].astype(int)
            txs_df['gasPrice'] = txs_df['gasPrice'].astype(np.int64)
            txs_df['isError'] = txs_df['isError'].astype(int)
            txs_df['cumulativeGasUsed'] = txs_df['cumulativeGasUsed'].astype(int)
            txs_df['gasUsed'] = txs_df['gasUsed'].astype(int)
            txs_df['confirmations'] = txs_df['confirmations'].astype(int)

            txs_df['hash'] = txs_df['hash'].str.lower()
            txs_df['blockHash'] = txs_df['blockHash'].str.lower()
            txs_df['from'] = txs_df['from'].str.lower()
            txs_df['to'] = txs_df['to'].str.lower()
            txs_df['blockHash'] = txs_df['blockHash'].str.lower()

        else:
            raise ValueError("No transactions found")

        txs_df = txs_df[txs_df['isError'] != 1]
        txs_df.reset_index(drop=True, inplace=True)

        txs_df['txType'] = txs_df.apply(
            lambda row: self.classify_tx(row['from'], row['to'], row['methodId'], row['value']),
            axis=1)

        token_txs_list = get_token_txs(self.wallet, api_endpoint, startblock=startblock)

        token_txs_df = pd.DataFrame(token_txs_list)

        if token_txs_df.shape[0] != 0:
            token_txs_df['blockNumber'] = token_txs_df['blockNumber'].astype(int)
            token_txs_df['timeStamp'] = token_txs_df['timeStamp'].astype(int)
            token_txs_df['hash'] = token_txs_df['hash'].str.lower()
            token_txs_df['nonce'] = token_txs_df['nonce'].astype(int)
            token_txs_df['blockHash'] = token_txs_df['blockHash'].str.lower()
            token_txs_df['from'] = token_txs_df['from'].str.lower()
            token_txs_df['contractAddress'] = token_txs_df['contractAddress'].str.lower()
            token_txs_df['to'] = token_txs_df['to'].str.lower()

            # Delete all rows where tokenDecimal is '' to avoid errors with astype()
            token_txs_df = token_txs_df[token_txs_df['tokenDecimal'] != '']
            token_txs_df['tokenDecimal'] = token_txs_df['tokenDecimal'].astype(int)

            # Numbers too big even for np.int64, workaround: delete n-1 last characters, n=tokenDecimal
            token_txs_df['value'] = token_txs_df.apply(
                lambda row: self.change_decimal(row['value'], row['tokenDecimal'], 2), axis=1)

            token_txs_df['value'] = token_txs_df['value'].astype(float)

            token_txs_df['tokenName'] = token_txs_df['tokenName'].str.lower()
            token_txs_df['tokenSymbol'] = token_txs_df['tokenSymbol'].str.lower()
            token_txs_df['transactionIndex'] = token_txs_df['transactionIndex'].astype(int)
            token_txs_df['gas'] = token_txs_df['gas'].astype(int)
            token_txs_df['gasPrice'] = token_txs_df['gasPrice'].astype(np.int64)
            token_txs_df['gasUsed'] = token_txs_df['gasUsed'].astype(int)
            token_txs_df['cumulativeGasUsed'] = token_txs_df['cumulativeGasUsed'].astype(int)
            token_txs_df['confirmations'] = token_txs_df['confirmations'].astype(int)

        internal_txs_list = get_internal_txs(self.wallet, api_endpoint, startblock=startblock)

        internal_txs_df = pd.DataFrame(internal_txs_list)

        if internal_txs_df.shape[0] != 0:
            internal_txs_df['blockNumber'] = internal_txs_df['blockNumber'].astype(int)
            internal_txs_df['timeStamp'] = internal_txs_df['timeStamp'].astype(int)
            internal_txs_df['hash'] = internal_txs_df['hash'].str.lower()
            internal_txs_df['from'] = internal_txs_df['from'].str.lower()
            internal_txs_df['to'] = internal_txs_df['to'].str.lower()
            internal_txs_df['value'] = internal_txs_df.apply(
                lambda row: self.change_decimal(row['value'], 18, 8), axis=1)

            internal_txs_df['value'] = internal_txs_df['value'].astype(float)

            internal_txs_df['contractAddress'] = internal_txs_df['contractAddress'].str.lower()
            internal_txs_df['type'] = internal_txs_df['type'].str.lower()
            internal_txs_df['gas'] = internal_txs_df['gas'].astype(int)
            internal_txs_df['gasUsed'] = internal_txs_df['gasUsed'].astype(int)
            internal_txs_df['isError'] = internal_txs_df['isError'].astype(int)
            internal_txs_df['traceId'] = internal_txs_df['traceId'].str.lower()
            internal_txs_df['errCode'] = internal_txs_df['errCode'].str.lower()

        self.txs_df = txs_df
        self.token_txs_df = token_txs_df
        self.internal_txs_df = internal_txs_df

    def change_decimal(self, value: str, decimal: int, crop: int = 1) -> float:
        """
        Change the decimal of the value. Walkaround for the numbers that are too big even for np.int64.
        Most tokens decimal is 18, this function can change the value to a smaller value by loosing precision.
        :param value: value to change
        :param decimal: current length of the value
        :param crop: how many last digits to crop
        :return: float value with the new decimal
        """
        try:
            change = decimal - crop
            value = value[: -change]
            value_float = float(value) / 10 ** crop
        except ValueError:
            value_float = 0.0

        return value_float

    def classify_tx(self, from_wallet: str, to_wallet: str, method_id: str, value: int) -> str:
        """
        Check what type of tx is it
        :param from_wallet: from wallet address
        :param to_wallet: to wallet address
        :param method_id: method id
        :param value: value of the transaction (ETH)
        :return: type of the tx
        """

        if from_wallet == self.wallet and value != 0 and method_id == '0x':
            tx_type = 'eth_transfer_out'

        elif to_wallet == self.wallet and value != 0 and method_id == '0x':
            tx_type = 'eth_transfer_in'

        elif method_id == '0x095ea7b3':
            tx_type = 'approve'

        elif any(to_wallet == router for router in self.routers) and value == 0:
            tx_type = 'swap_tx_zero_value'

        elif any(to_wallet == router for router in self.routers) and value != 0:
            tx_type = 'swap_tx_nonzero_value'

        else:
            tx_type = 'other'

        return tx_type


if __name__ == "__main__":
    wallet_analyzer = WalletAnalyzer("0x7e5e597c3005037246f9efdb61f79d193d1d546c")
    wallet_analyzer.get_data()