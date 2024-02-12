"""Analysis of a ETH wallet"""
import datetime
import os

from download_wallet_txs import get_txs, get_token_txs, get_internal_txs
import pandas as pd
import numpy as np


class WalletAnalyzer:
    def __init__(self, wallet: str, chain='eth') -> None:
        """
        Analyzes wallet transactions
        :param wallet: wallet address
        """
        self.weth_address = '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'
        self.wallet = wallet.lower()
        self.chain = chain

        self.txs_df = None
        self.token_txs_df = None
        self.internal_txs_df = None

        if self.chain == 'eth':
            uniswap_universal_router_address = '0x3fC91A3afd70395Cd496C647d5a6CC9D4B2b7FAD'.lower()

            uniswap_old_universal_router = '0xEf1c6E67703c7BD7107eed8303Fbe6EC2554BF6B'.lower()
            uniswap_v2_router_2_address = '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D'.lower()
            uniswap_v3_router_2_address = '0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45'.lower()
            sushiswap_router_address = '0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F'.lower()
            inch_v5_aggregation_router_address = '0x1111111254EEB25477B68fb85Ed929f73A960582'.lower()
            metamask_swap_router = '0x881D40237659C251811CEC9c364ef91dC08D300C'.lower()
            kyberswap_meta_aggregation_router_v2 = '0x6131B5fae19EA4f9D964eAc0408E4408b66337b5'.lower()
            rainbow_router = '0x00000000009726632680FB29d3F7A9734E3010E2'.lower()

            self.routers = [uniswap_v2_router_2_address, uniswap_v3_router_2_address, sushiswap_router_address,
                            uniswap_old_universal_router, inch_v5_aggregation_router_address, metamask_swap_router,
                            kyberswap_meta_aggregation_router_v2, rainbow_router, uniswap_universal_router_address]

            # Source: https://ethplorer.io/tag/stablecoins#
            self.stablecoins = ["0xdac17f958d2ee523a2206206994597c13d831ec7",
                                "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
                                "0x6b175474e89094c44da98b954eedeac495271d0f",
                                "0x8e870d67f660d95d5be530380d0ec0bd388289e1",
                                "0x4fabb145d64652a948d72533023f6e7a623c7c53",
                                "0x0000000000085d4780b73119b644ae5ecd22b376",
                                "0xa47c8bf37f92abed4a126bda807a7b7498661acd",
                                "0x853d955acef822db058eb8505911ed77f175b99e",
                                "0x056fd409e1d7a124bd7017459dfea2f387b6d5cd",
                                "0x57ab1ec28d129707052df4df418d58a2d46d5f51"]

        # For the implementation of the BSC chain
        elif self.chain == 'bsc':
            pancakeswap_v2_universal_router = '0x10ED43C718714eb63d5aA57B78B54704E256024E'.lower()
            pancakeswap_v3_universal_router = '0x13f4EA83D0bd40E75C8222255bc855a974568Dd4'.lower()
            kyberswap_meta_aggregation_router_v2 = '0x6131B5fae19EA4f9D964eAc0408E4408b66337b5'.lower()
            metamask_swap_router = '0x1a1ec25DC08e98e5E93F1104B5e5cdD298707d31'.lower()
            rainbow_router = '0x00000000009726632680FB29d3F7A9734E3010E2'.lower()
            apeswap_router = '0xC0788A3aD43d79aa53B09c2EaCc313A787d1d607'.lower()
            bakeryswap_router = '0xCDe540d7eAFE93aC5fE6233Bee57E1270D3E330F'.lower()
            beltfinance_router = '0x9cb73F20164e399958261c289Eb5F9846f4D1404'.lower()
            burger_swap_router = '0x58F876857a02D6762E0101bb5C46A8c1ED44Dc16'.lower()
            cafeswap_router = '0x933DAea3a5995Fb94b14A7696a5F3ffD7B1E385A'.lower()
            cakedefi_router = '0x0ED7e52944161450477ee417DE9Cd3a859b14fD0'.lower()
            crowfinance_router = '0x3e9c2ee838072b370567efc2df27602d776b341c'.lower()
            dopple_router = '0x029f944cd3afa7c229122b19c706d8f9c6bcc963'.lower()
            ellipsis_router = '0x160CAed03795365F3A589f10C379FfA7d75d4E76'.lower()
            sushiswap_router_address = '0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506'.lower()

            self.routers = [pancakeswap_v2_universal_router, pancakeswap_v3_universal_router, rainbow_router,
                            apeswap_router, bakeryswap_router, beltfinance_router, burger_swap_router, cafeswap_router,
                            cakedefi_router, crowfinance_router, dopple_router, ellipsis_router,
                            sushiswap_router_address, kyberswap_meta_aggregation_router_v2, metamask_swap_router]

            self.stablecoins = ["0xe9e7cea3dedca5984780bafc599bd69add087d56",
                                "0x55d398326f99059ff775485246999027b3197955",
                                "0x1af3f329e8be154074d8769d1ffa4ee058b1dbc3",
                                "0x2170ed0880ac9a755fd29b2688956bd959f933f8",
                                "0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d",
                                "0x55d398326f99059ff775485246999027b3197955",
                                "0x23396cf899ca06c4472205fc903bdb4de249d6fc",
                                "0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d",
                                "0x55d398326f99059fF775485246999027B3197955"]

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

    def move_weth_transactions(self) -> None:
        """
        Move WETH transactions from token_txs_df to the txs_df
        :return: None
        """
        weth_txs = self.token_txs_df.loc[self.token_txs_df['contractAddress'] == self.weth_address]

        # Delete WETH transactions from token_txs_df
        self.token_txs_df = self.token_txs_df.loc[~self.token_txs_df['hash'].isin(weth_txs['hash'])]

        # For every WETH transaction, change the 'value' and 'txType' in the txs_df - locate the transaction by hash
        for index, row in weth_txs.iterrows():
            self.txs_df.loc[self.txs_df['hash'] == row['hash'], 'value'] = row['value']

            if row['from'] == self.wallet:
                self.txs_df.loc[self.txs_df['hash'] == row['hash'], 'txType'] = 'swap_tx_nonzero_value'

            else:
                self.txs_df.loc[self.txs_df['hash'] == row['hash'], 'txType'] = 'swap_tx_zero_value'

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

    def save_data(self, folder: str = "data") -> None:
        """
        Save the txs_df, token_txs_df and internal_txs_df dataframes to separate CSV files in the given dir
        :param folder: directory of the files
        :return: None
        """
        self.txs_df.to_csv(folder + f'/{self.wallet}_txs_df.csv', sep='\t', encoding='utf-8')
        self.token_txs_df.to_csv(folder + f'/{self.wallet}_token_txs_df.csv', sep='\t', encoding='utf-8')
        self.internal_txs_df.to_csv(folder + f'/{self.wallet}_internal_txs_df.csv', sep='\t', encoding='utf-8')

    def load_data(self, folder: str = "data") -> None:
        """
        Same as self.get_data but loads the data from 3 CSV files located in the dir
        :param folder: directory of the files
        :return: None
        """
        self.txs_df = pd.read_csv(folder + f'/{self.wallet}_txs_df.csv', sep='\t', encoding='utf-8')
        self.token_txs_df = pd.read_csv(folder + f'/{self.wallet}_token_txs_df.csv', sep='\t', encoding='utf-8')
        self.internal_txs_df = pd.read_csv(folder + f'/{self.wallet}_internal_txs_df.csv', sep='\t', encoding='utf-8')

    def calculate_swap_txs(self) -> None:
        """
        Get the data about the trades from the token transactions df
        :return: None
        """

        # swap buy - when tx send ETH from self.wallet and token_tx send tokens in self.wallet
        # swap sell - when internal_tx send ETH in self.wallet and token_tx send tokens from self.wallet
        self.txs_df[['swapType', 'swapEth', 'tokenValue', 'tokenName', 'tokenSymbol', 'tokenCa',
                     'tokenDecimal']] = self.txs_df.apply(
            lambda row: self.get_info_from_token_txs(row['hash'], row['txType'], row['value']),
            axis=1)

    def get_info_from_token_txs(self, tx_hash: str, tx_type: str, value: float) -> pd.Series:
        """
        Get information about the transaction for the token_txs_df. Use it to merge data of txs_df with token_txs_df.
        :param tx_hash: Transaction hash
        :param tx_type: Transaction type
        :param value: Transaction value
        :return: Series with the information about the transaction
        """

        tx = self.token_txs_df[self.token_txs_df['hash'] == tx_hash]

        token_value = np.nan
        token_name = np.nan
        token_symbol = np.nan
        token_decimal = np.nan
        token_ca = np.nan
        swap_type = np.nan
        swap_eth = np.nan

        try:
            # buy
            if tx_type == 'swap_tx_nonzero_value':
                if tx.shape[0] == 1:
                    if tx['to'].item() == self.wallet:
                        token_value = tx['value'].item()
                        token_name = tx['tokenName'].item()
                        token_symbol = tx['tokenSymbol'].item()
                        token_decimal = tx['tokenDecimal'].item()
                        token_ca = tx['contractAddress'].item()
                        swap_type = 'swap_buy'
                        swap_eth = value
            # sell
            elif tx_type == 'swap_tx_zero_value':
                # Find ETH in internal txs
                internal_tx = self.internal_txs_df[self.internal_txs_df['hash'] == tx_hash]
                if internal_tx.shape[0] == 1:
                    if internal_tx['to'].item() == self.wallet:
                        swap_type = 'swap_sell'
                        swap_eth = internal_tx['value'].item()

                        # Get token info
                        token_value = tx['value'].sum()
                        token_name = tx['tokenName'].iloc[0]
                        token_symbol = tx['tokenSymbol'].iloc[0]
                        token_decimal = tx['tokenDecimal'].iloc[0]
                        token_ca = tx['contractAddress'].iloc[0]

            elif tx_type == 'other':
                # OTHER BUY
                if tx.shape[0] == 1:
                    if tx['to'].item() == self.wallet and value != 0:
                        token_value = tx['value'].item()
                        token_name = tx['tokenName'].item()
                        token_symbol = tx['tokenSymbol'].item()
                        token_decimal = tx['tokenDecimal'].item()
                        token_ca = tx['contractAddress'].item()
                        swap_type = 'other_buy'
                        swap_eth = value
                else:
                    # OTHER SELL
                    internal_tx = self.internal_txs_df[self.internal_txs_df['hash'] == tx_hash]

                    if internal_tx.shape[0] == 1:
                        if internal_tx['to'].item() == self.wallet and value == 0:
                            swap_type = 'other_sell'
                            swap_eth = internal_tx['value'].item()

                            # Get token info
                            token_value = tx['value'].sum()
                            token_name = tx['tokenName'].iloc[0]
                            token_symbol = tx['tokenSymbol'].iloc[0]
                            token_decimal = tx['tokenDecimal'].iloc[0]

            elif tx_type == 'tokens_transfer_out':
                swap_type = np.nan
                swap_eth = np.nan

                # Get token info
                if tx.shape[0] > 0:
                    token_value = tx['value'].sum()
                    token_name = tx['tokenName'].iloc[0]
                    token_symbol = tx['tokenSymbol'].iloc[0]
                    token_decimal = tx['tokenDecimal'].iloc[0]
                    token_ca = tx['contractAddress'].iloc[0]
        except IndexError:
            pass

        return pd.Series([swap_type, swap_eth, token_value, token_name, token_symbol, token_ca, token_decimal],
                         index=['swapType', 'swapEth', 'tokenValue', 'tokenName', 'tokenSymbol', 'tokenCa',
                                'tokenDecimal'])

    def check_snipers(self, max_allowed_overshoot: float = 1.6) -> None:
        """
        Mark the snipe transactions (with high gas price)
        :param max_allowed_overshoot: Max allowed gas price overshoot (compared to the avg gas price in the selected day)
        :return: None
        """
        current_location = os.path.dirname(os.path.realpath(__file__))

        gas_price_df = self.load_gas_price_history(os.path.join(current_location, 'data/export-AvgGasPrice.csv'))
        # Check every txs_df record if the gasPrice is greater than max_allowed_overshoot*avg gas price in the selected day
        self.txs_df['dateTime'] = pd.to_datetime(self.txs_df['timeStamp'], unit='s')
        self.txs_df['date_only'] = self.txs_df['dateTime'].dt.date
        self.txs_df['date_only'] = pd.to_datetime(self.txs_df['date_only'])
        self.txs_df = pd.merge(self.txs_df, gas_price_df, left_on='date_only', right_on='date', how='left')

        # Fill the None values
        self.txs_df['avgGasPrice'] = self.txs_df['avgGasPrice'].fillna(99999999999)

        self.txs_df['snipe'] = (self.txs_df['gasPrice'] > max_allowed_overshoot * self.txs_df['avgGasPrice']) & (
                self.txs_df['swapType'] == 'swap_buy')

        self.txs_df = self.txs_df.drop(columns=['date_only', 'date', 'avgGasPrice'])

    def load_gas_price_history(self, file='data/export-AvgGasPrice.csv') -> pd.DataFrame:
        """
        Load gas price history (export data from Etherscan.io)
        :param file: CSV file with gas price history
        :return: dataframe with gas price history
        """
        gas_price_df = pd.read_csv(file, header=0)

        gas_price_df["date"] = pd.to_datetime(gas_price_df["Date(UTC)"])
        gas_price_df["avgGasPrice"] = gas_price_df["Value (Wei)"].astype(np.int64)
        gas_price_df = gas_price_df.drop(columns=["UnixTimeStamp", "Date(UTC)", "Value (Wei)"])

        return gas_price_df

    def get_swap_txs(self, drop_snipes: bool = False, include_other_swap_types: bool = False,
                     drop_in_out_tokens: bool = False, drop_stablecoins_swaps: bool = True) -> pd.DataFrame:
        """
        Get all the swap transactions (buy and sell) from the txs_df
        :param drop_snipes: whether to drop all transaction of tokens that have snipe transactions
        :param include_other_swap_types: whether to include other swap types (other_buy, other_sell)
        :param drop_in_out_tokens: whether to drop all transaction of tokens that have in/out transactions
        :param drop_stablecoins_swaps: whether to drop stablecoins swaps
        :return: dataframe with all the swap transactions
        """

        # Other swap types means swaps that are not made via known router, but looks like they are trades
        if include_other_swap_types:
            swap_txs_df = self.txs_df.loc[
                (self.txs_df['swapType'] == 'swap_buy') | (self.txs_df['swapType'] == 'swap_sell')
                | (self.txs_df['swapType'] == 'other_buy') | (self.txs_df['swapType'] == 'other_sell')]
        else:
            swap_txs_df = self.txs_df.loc[
                (self.txs_df['swapType'] == 'swap_buy') | (self.txs_df['swapType'] == 'swap_sell')]

        # Drop snipes (every token that has at least 1 tx like that)
        if drop_snipes:
            swap_txs_df = self.drop_snipes(swap_txs_df)

        # Drop all tokens that have in/out transactions
        if drop_in_out_tokens:
            swap_txs_df = self.drop_in_out_tokens(swap_txs_df)

        # Do not consider stablecoins swaps
        if drop_stablecoins_swaps:
            swap_txs_df = swap_txs_df.loc[~swap_txs_df['tokenCa'].isin(self.stablecoins)]

        return swap_txs_df

    def drop_snipes(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove all the transactions with tokens that have at least 1 snipe transaction
        :param df: dataframe with all the transactions
        :return: dataframe with all the transactions with tokens with snipe transactions removed
        """
        snipes_ca_list = self.txs_df.loc[self.txs_df['snipe'] == True, 'tokenCa'].unique()

        df = df.loc[~df['tokenCa'].isin(snipes_ca_list)]

        return df

    def drop_in_out_tokens(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove all the transactions with tokens that have at least 1 in/out transaction
        :param df: dataframe with all the transactions
        :return: dataframe with all the transactions with tokens with in/out transactions removed
        """
        in_out_tokens_list = self.txs_df.loc[(self.txs_df['txType'] == 'tokens_transfer_in') | (
                self.txs_df['txType'] == 'tokens_transfer_out'), 'tokenCa'].unique()

        df = df.loc[~df['tokenCa'].isin(in_out_tokens_list)]

        return df

    def check_token_transfers(self) -> None:
        """
        Check for token transfers in and out (including stablecoins)
        :return: None
        """
        # Incoming transfers - only in 'token transfers' tab
        # Check for tx hashes in self.token_txs_df that are not in the self.txs_df
        try:
            incoming_transfers_df = self.token_txs_df.loc[~self.token_txs_df['hash'].isin(self.txs_df['hash'])].copy()

            # Make sure tokens go to the self.wallet
            incoming_transfers_df = incoming_transfers_df[incoming_transfers_df['to'] == self.wallet]
            incoming_transfers_df['txType'] = 'tokens_transfer_in'

            incoming_transfers_df.loc[
                incoming_transfers_df['contractAddress'].isin(self.stablecoins), 'txType'] = 'stablecoins_transfer_in'
            incoming_transfers_df['tokenValue'] = incoming_transfers_df['value'].astype(float)
            incoming_transfers_df['value'] = 0
            incoming_transfers_df['isError'] = 0
            incoming_transfers_df.rename(columns={'contractAddress': 'tokenCa'}, inplace=True)

            self.txs_df = pd.concat([self.txs_df, incoming_transfers_df])

        except KeyError:
            pass

        # Out-coming transfers - in 'transactions' tab, additional info from 'token transfers' tab
        # Just copy info from 'token transfers' df to the 'transfers' df for the rows where 'txType' == 'other',
        # 'from' == self.wallet, 'value' == 0
        try:
            self.txs_df.loc[(self.txs_df['txType'] == 'other') & (self.txs_df['from'] == self.wallet) & (
                    self.txs_df['value'] == 0), 'txType'] = 'tokens_transfer_out'

            tokens_transfer_out_df = self.txs_df.loc[self.txs_df['txType'] == 'tokens_transfer_out'].copy()

            tokens_transfer_out_df.loc[:, ['swapType', 'swapEth', 'tokenValue', 'tokenName', 'tokenSymbol', 'tokenCa',
                                           'tokenDecimal']] = tokens_transfer_out_df.apply(
                lambda row: self.get_info_from_token_txs(row['hash'], 'tokens_transfer_out', 0), axis=1)

            tokens_transfer_out_df.loc[(tokens_transfer_out_df['tokenCa'].isin(self.stablecoins)) & (
                    tokens_transfer_out_df[
                        'txType'] == 'tokens_transfer_out'), 'txType'] = 'stablecoins_transfer_out'

            tokens_transfer_out_df.set_index('hash', inplace=True)
            self.txs_df.set_index('hash', inplace=True)

            self.txs_df.update(tokens_transfer_out_df)

            self.txs_df.reset_index(inplace=True)

        except KeyError:
            pass

    def calculate_tokens_txs(self, drop_snipes: bool = False, include_other_swap_types: bool = False,
                             drop_in_out_tokens: bool = False) -> pd.DataFrame:
        """
        Creates self.token_trades df containing aggregated info about trades per every token
        :param drop_snipes:
        :param include_other_swap_types:
        :param drop_in_out_tokens:
        :return: Dataframe with aggregated info about trades per every token and trading metrics per token
        """

        # other swap types means swaps that are not made via known router, but looks like they are trades
        swap_txs_df = self.get_swap_txs(drop_snipes, include_other_swap_types, drop_in_out_tokens)

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

    def check_internal_transfers(self) -> None:
        """
        For ETH transfers via contracts
        :return: None
        """

        # Incoming ETH transfers
        try:
            incoming_transfers_df = self.internal_txs_df.loc[
                ~self.internal_txs_df['hash'].isin(self.txs_df['hash'])].copy()
        except KeyError:
            return

        # Make sure tokens go to the self.wallet
        incoming_transfers_df = incoming_transfers_df[incoming_transfers_df['to'] == self.wallet]
        incoming_transfers_df['txType'] = 'eth_other_transfer_in'

        self.txs_df = pd.concat([self.txs_df, incoming_transfers_df])

        self.txs_df = self.txs_df.drop(columns=['type', 'traceId', 'errCode'])

    def select_data_by_timestamp(self, start=None, stop=None) -> None:
        """
        Select only trades in a given timeframe
        :param start: start timestamp
        :param stop: stop timestamp
        :return: None
        """

        if start:
            self.txs_df = self.txs_df.loc[self.txs_df['timeStamp'] >= start]
            self.token_txs_df = self.token_txs_df.loc[self.token_txs_df['timeStamp'] >= start]

            if 'timeStamp' in self.internal_txs_df.columns:
                self.internal_txs_df = self.internal_txs_df.loc[self.internal_txs_df['timeStamp'] >= start]

        if stop:
            self.txs_df = self.txs_df.loc[self.txs_df['timeStamp'] <= stop]
            self.token_txs_df = self.token_txs_df.loc[self.token_txs_df['timeStamp'] <= stop]

            if 'timeStamp' in self.internal_txs_df.columns:
                self.internal_txs_df = self.internal_txs_df.loc[self.internal_txs_df['timeStamp'] <= stop]


class MetricsCalculator:
    def __init__(self, swap_txs_df: pd.DataFrame, txs_df: pd.DataFrame, token_trades_df: pd.DataFrame):
        self.token_trades_df = token_trades_df
        self.swap_txs_df = swap_txs_df
        self.txs_df = txs_df

    def first_tx_datetime(self) -> datetime.datetime:
        """
        Get the datetime of the first transaction
        :return: datetime of the first transaction
        """

        first_tx_datetime = self.txs_df.loc[:, 'timeStamp'].min()

        return datetime.datetime.fromtimestamp(first_tx_datetime)

    def last_tx_datetime(self) -> datetime.datetime:
        """
        Get the datetime of the last transaction
        :return: datetime of the last transaction
        """

        last_tx_datetime = self.txs_df.loc[:, 'timeStamp'].max()

        return datetime.datetime.fromtimestamp(last_tx_datetime)

    def avg_trade_result(self, perc: bool = False) -> float:
        """
        How big is the average result of a trade (in ETH or %). Only for trades that have both buy&sell transactions!
        :param perc: whether to return the result in % (if False, in ETH)
        :return: average result of trade in ETH or %. 100% means you gained 0 ETH
        """
        assert self.token_trades_df is not None, 'Use self.calculate_tokens_txs() first!'

        if perc:
            avg_trade_result = self.token_trades_df.loc[:, 'tradeResultPercentage'].mean()
        else:
            avg_trade_result = self.token_trades_df.loc[:, 'ethResult'].mean()

        return avg_trade_result

    def win_ratio_percent(self) -> float:
        """
        How many trades were profitable (in %)
        :return: percentage of profitable trades
        """
        df = self.token_trades_df
        df1 = df.groupby(level=0).size().reset_index(name='txs_number2')
        df1 = df1.set_index('tokenCa')

        token_ca = df.index.get_level_values('tokenCa')
        df['txsNumber'] = df1.loc[token_ca].values

        df.loc[df['txsNumber'] == 1, 'tradeResultPercentage'] = 0

        df.loc[df['tradeResultPercentage'] > 100, 'win'] = True
        df.loc[df['tradeResultPercentage'] <= 100, 'win'] = False

        win_number = len(df[df['win'] == True])
        lose_number = len(df[df['win'] == False])

        return win_number * 100 / (win_number + lose_number)

    def final_trade_result(self) -> float:
        """
        Final trade result based on the self.token_trades, only for tokens that have both buy and sell txs
        :return: final trade result in ETH
        """

        # Only for tokens that have both sell and buy transactions!
        assert self.token_trades_df is not None, 'Use self.calculate_tokens_txs() first!'

        final_trading_eth_result = self.token_trades_df['ethResult'].sum()

        return final_trading_eth_result

    def avg_trade_size(self) -> float:
        """
        How big is the average bet (in ETH)
        :return: average buy order size in ETH
        """
        assert self.token_trades_df is not None, 'Use self.calculate_tokens_txs() first!'

        buy_orders_number = self.token_trades_df.xs('swap_buy', level=1, drop_level=False)['orders'].sum()
        buy_orders_value = self.token_trades_df.xs('swap_buy', level=1, drop_level=False)['swapEth'].sum()

        return buy_orders_value / buy_orders_number

    def snipes_percent(self) -> float:
        """
        How many swaps were snipes (with high gas fee)
        :return: percentage of snipe transactions
        """

        snipes_number = self.txs_df.loc[self.txs_df['snipe'] == True].shape[0]
        total_trades_number = self.txs_df.shape[0]

        return snipes_number * 100 / total_trades_number

    def trades_per_day(self) -> pd.DataFrame:
        """
        Calculate how many trades were made every day
        :return: dataframe with the number of trades per day
        """
        self.swap_txs_df['date'] = pd.to_datetime(self.swap_txs_df.loc[:, 'timeStamp'], unit='s').dt.date

        trades_per_day_df = self.swap_txs_df.groupby(['date'])['hash'].count()

        trades_per_day_df = trades_per_day_df.to_frame().reset_index()

        trades_per_day_df = trades_per_day_df.rename(columns={'hash': 'trades_number'})
        trades_per_day_df.index.name = 'index'

        return trades_per_day_df

    def cumulated_daily_trading_result(self) -> pd.DataFrame:
        """
        Cumulative daily trading result (total sell-buy)
        :return: dataframe with the cumulated daily trading result
        """

        swap_txs_df = self.swap_txs_df.sort_values(by=['timeStamp'])

        swap_txs_df['date'] = pd.to_datetime(swap_txs_df.loc[:, 'timeStamp'], unit='s').dt.date

        swap_txs_df['cumBuy'] = swap_txs_df.loc[swap_txs_df['swapType'] == 'swap_buy', 'swapEth'].cumsum()
        swap_txs_df['cumSell'] = swap_txs_df.loc[swap_txs_df['swapType'] == 'swap_sell', 'swapEth'].cumsum()

        # Fill nan values with the last cumulative value
        swap_txs_df['cumBuy'] = swap_txs_df['cumBuy'].fillna(method='ffill')
        swap_txs_df['cumSell'] = swap_txs_df['cumSell'].fillna(method='ffill')

        # Reset index
        swap_txs_df.reset_index(inplace=True)

        # Fill nan with 0
        swap_txs_df['cumBuy'] = swap_txs_df['cumBuy'].fillna(0)
        swap_txs_df['cumSell'] = swap_txs_df['cumSell'].fillna(0)

        swap_txs_df['cumResult'] = swap_txs_df['cumSell'] - swap_txs_df['cumBuy']

        return swap_txs_df

    def median_trade_size(self) -> float:
        """
        How big is the median bet (in ETH)
        :return: median buy order size in ETH
        """
        assert self.swap_txs_df is not None, 'Use self.get_data() first!'

        median_trade_size = self.swap_txs_df.loc[self.swap_txs_df['swapType'] == 'swap_buy', 'swapEth'].median()

        return median_trade_size

    def first_trade_datetime(self) -> datetime.datetime:
        """
        Get the datetime of the first transaction
        :return: datetime of the first transaction
        """
        assert self.swap_txs_df is not None, 'Use self.get_data() first!'

        first_swap_datetime = self.swap_txs_df.loc[:, 'timeStamp'].min()

        return datetime.datetime.fromtimestamp(first_swap_datetime)

    def last_trade_datetime(self) -> datetime.datetime:
        """
        Get the datetime of the last trade
        :return: datetime of the last trade
        """
        assert self.swap_txs_df is not None, 'Use self.get_data() first!'

        last_swap_datetime = self.swap_txs_df.loc[:, 'timeStamp'].max()

        return datetime.datetime.fromtimestamp(last_swap_datetime)

    def total_swaps_number(self) -> int:
        """
        How many swaps were made in total
        :return: number of swaps made in total
        """
        assert self.swap_txs_df is not None, 'Use self.get_data() first!'

        return len(self.swap_txs_df.index)

    def traded_tokens_number(self) -> int:
        """
        How many tokens were traded in total
        :return: number of tokens traded in total
        """

        traded_tokens_number = self.swap_txs_df['tokenCa'].nunique()

        return traded_tokens_number

    def calculate_total_values(self):
        """
        Calculate total in,out and buy,sell on DEX
        :return: total_eth_in, total_eth_out, total_eth_buy, total_eth_sell
        """
        # Calculate total values
        total_eth_out = self.txs_df.loc[self.txs_df['txType'] == 'eth_transfer_out', 'value'].sum()
        total_eth_in = self.txs_df.loc[self.txs_df['txType'] == 'eth_transfer_in', 'value'].sum()
        total_eth_internal_in = self.txs_df.loc[self.txs_df['txType'] == 'eth_other_transfer_in', 'value'].sum()

        total_eth_buy = self.swap_txs_df.loc[self.swap_txs_df['swapType'] == 'swap_buy', 'swapEth'].sum()
        total_eth_sell = self.swap_txs_df.loc[self.swap_txs_df['swapType'] == 'swap_sell', 'swapEth'].sum()

        total_stablecoins_in = self.txs_df.loc[self.txs_df['txType'] == 'stablecoins_transfer_in', 'tokenValue'].sum()
        total_stablecoins_out = self.txs_df.loc[self.txs_df['txType'] == 'stablecoins_transfer_out', 'tokenValue'].sum()

        count_tokens_in = self.txs_df.loc[self.txs_df['txType'] == 'tokens_transfer_in', 'hash'].count()
        count_tokens_out = self.txs_df.loc[self.txs_df['txType'] == 'tokens_transfer_put', 'hash'].count()

        # Fees paid
        self.txs_df['txFee'] = self.txs_df['gasPrice'] / 10 ** 18 * self.txs_df['gasUsed']
        total_fees_eth = self.txs_df.loc[
            (self.txs_df['swapType'] == 'swap_buy') | (self.txs_df['swapType'] == 'swap_sell'), 'txFee'].sum()

        return total_eth_in, total_eth_internal_in, total_eth_out, total_eth_buy, total_eth_sell, total_stablecoins_in,\
            total_stablecoins_out, total_fees_eth, count_tokens_in, count_tokens_out

    def calculate_rolling_ratings(self) -> pd.DataFrame:
        """
        Calculates different types of ratings after every trade
        :return: dataframe with the ratings
        """
        assert self.swap_txs_df is not None, 'Use self.get_data() first!'

        swap_txs_df = self.swap_txs_df.sort_values(by='blockNumber', ascending=True)

        swap_txs_df = swap_txs_df.reset_index(drop=True)

        # Trades last 7d -----------------------------------------
        def trades_last_7d(data_series):
            # The current day in the expanding window
            current_day = data_series.iloc[-1]

            # Filter the trades in the last 7 days
            last_7_days_trades = data_series[data_series >= (current_day - 7)]

            return len(last_7_days_trades)

        # Create a column 'days_since_start' representing the number of days since the earliest date (temporary col)
        swap_txs_df['days_since_start'] = (swap_txs_df['dateTime'] - swap_txs_df['dateTime'].min()).dt.days

        swap_txs_df['trades_last_7d'] = swap_txs_df['days_since_start'].expanding().apply(trades_last_7d)

        swap_txs_df = swap_txs_df.drop(columns=['days_since_start'])

        # Total traded tokens number ------------------------------
        # Initialize an empty set to store unique tokens and a list to store cumulative counts
        unique_tokens_seen = set()
        cumulative_unique_tokens = []

        # Iterate through the dataframe and calculate cumulative unique tokens
        for token in swap_txs_df['tokenCa']:
            unique_tokens_seen.add(token)
            cumulative_unique_tokens.append(len(unique_tokens_seen))

        # Add the cumulative counts to the dataframe
        swap_txs_df['unique_tokens_traded_number'] = cumulative_unique_tokens

        # Total swaps number --------------------------------------
        swap_txs_df['total_swaps'] = range(1, len(swap_txs_df) + 1)

        # total sells value/total buy value ---
        swap_txs_df['buy_values'] = swap_txs_df['swapEth'].where(swap_txs_df['swapType'] == 'swap_buy', 0)
        swap_txs_df['sell_values'] = swap_txs_df['swapEth'].where(swap_txs_df['swapType'] == 'swap_sell', 0)

        # Calculate the cumulative sums for buys and sells separately
        swap_txs_df['cumulative_buys'] = swap_txs_df['buy_values'].expanding().sum()
        swap_txs_df['cumulative_sells'] = swap_txs_df['sell_values'].expanding().sum()

        # Calculate total_sells_value/total_buys_value ratio
        # To avoid division by zero add a small value (1e-10) to the denominator
        swap_txs_df['sell_buy_ratio'] = swap_txs_df['cumulative_sells'] / (swap_txs_df['cumulative_buys'] + 1e-10)

        # Win ratio -----------------------------------------------
        # Calculate cumulative token buy and sell values
        swap_txs_df['token_buy_values'] = swap_txs_df['tokenValue'].where(swap_txs_df['swapType'] == 'swap_buy', 0)
        swap_txs_df['token_sell_values'] = swap_txs_df['tokenValue'].where(swap_txs_df['swapType'] == 'swap_sell', 0)
        swap_txs_df['cumulative_token_buys'] = swap_txs_df.groupby('tokenCa')['token_buy_values'].cumsum()
        swap_txs_df['cumulative_token_sells'] = swap_txs_df.groupby('tokenCa')['token_sell_values'].cumsum()

        # Check if the wallet have sold more than 90% of the tokens already
        swap_txs_df['sold_ratio'] = swap_txs_df['cumulative_token_sells'] / swap_txs_df['cumulative_token_buys']
        swap_txs_df['sold_more_than_90p'] = swap_txs_df['sold_ratio'] >= 0.9

        # For tokens with sold_more_than_90p check the ETH trading result
        swap_txs_df['eth_buy_values'] = swap_txs_df['swapEth'].where(swap_txs_df['swapType'] == 'swap_buy', 0)
        swap_txs_df['eth_sell_values'] = swap_txs_df['swapEth'].where(swap_txs_df['swapType'] == 'swap_sell', 0)
        swap_txs_df['cumulative_eth_buys'] = swap_txs_df.groupby('tokenCa')['eth_buy_values'].cumsum()
        swap_txs_df['cumulative_eth_sells'] = swap_txs_df.groupby('tokenCa')['eth_sell_values'].cumsum()

        swap_txs_df['eth_trade_result'] = swap_txs_df['cumulative_eth_sells'] - swap_txs_df['cumulative_eth_buys']
        swap_txs_df['eth_trade_result'] = np.where(swap_txs_df['sold_more_than_90p'] == True,
                                                   swap_txs_df['eth_trade_result'], np.nan)

        swap_txs_df['wins_number'] = swap_txs_df['eth_trade_result'] > 0
        swap_txs_df['total_trades_number'] = swap_txs_df['eth_trade_result'].notnull()

        swap_txs_df['wins_number_cumsum'] = swap_txs_df['wins_number'].cumsum()
        swap_txs_df['total_trades_number_cumsum'] = swap_txs_df['total_trades_number'].cumsum()

        swap_txs_df['win_ratio'] = swap_txs_df['wins_number_cumsum'] / swap_txs_df['total_trades_number_cumsum']

        # MA25 of win ratio
        swap_txs_df['win_ratio_ma25'] = swap_txs_df['wins_number'].rolling(window=25, min_periods=1).sum() / \
                                        swap_txs_df['total_trades_number'].rolling(window=25, min_periods=1).sum()

        # MA10 of trade result -------------------------------------------
        swap_txs_df['eth_trade_result_ma10'] = swap_txs_df['eth_trade_result'].rolling(window=10, min_periods=1).mean()

        # EXPANDING trade result -------------------------------------------
        swap_txs_df['eth_trade_result_expanding'] = swap_txs_df['eth_trade_result'].expanding().mean()

        # % of how many unique traded tokens have been already sold ------
        def calculate_tokens_with_90p_sold_up_to_index(idx, df):
            """
            Calculate the number of unique tokens that have been sold more than 90% up to a given index
            """
            relevant_slice = df.iloc[:idx + 1]
            tokens_sold_more_than_90p = relevant_slice[relevant_slice['sold_more_than_90p']]['tokenCa'].unique()
            return len(tokens_sold_more_than_90p)

        # Calculate the number of tokens with more than 90% sold for each row
        tokens_with_90p_sold_counts = [calculate_tokens_with_90p_sold_up_to_index(i, swap_txs_df) for i in
                                       range(len(swap_txs_df))]

        swap_txs_df['total_number_of_tokens_with_more_than_90p_sold'] = tokens_with_90p_sold_counts

        swap_txs_df['unique_tokens_already_sold_ratio'] = swap_txs_df[
                                                              'total_number_of_tokens_with_more_than_90p_sold'] / \
                                                          swap_txs_df['unique_tokens_traded_number']

        # Buy order size ---------------------------------------------
        swap_txs_df['buy_order_size'] = swap_txs_df['swapEth'].where(swap_txs_df['swapType'] == 'swap_buy', None)

        # Calculate the MA10 for buy order sizes
        swap_txs_df['buy_order_size_ma10'] = swap_txs_df['buy_order_size'].astype(float).rolling(window=10,
                                                                                                 min_periods=1).mean()

        # Buy order size EXPANDING AVERAGE --------------------------------
        swap_txs_df['buy_order_size_expanding_avg'] = swap_txs_df['buy_order_size'].astype(float).expanding().mean()

        # Eth trade result ma10 / buy order size ma10 ---------------------

        swap_txs_df['eth_trade_result_ma10/buy_order_size_ma10'] = swap_txs_df['eth_trade_result_ma10'] / swap_txs_df[
            'buy_order_size_ma10']

        # (total sells value-total buys value)/(number of swaps/2) --------
        swap_txs_df['profit_per_trade'] = (swap_txs_df['cumulative_sells'] - swap_txs_df['cumulative_buys']) / (
                swap_txs_df['total_swaps'] / 2 + 1e-10)

        # Fill na values in the columns with last record
        selected_columns = swap_txs_df[[
            "blockNumber",
            "trades_last_7d",
            "unique_tokens_traded_number",
            "total_swaps",
            "sell_buy_ratio",
            "win_ratio",
            "win_ratio_ma25",
            "eth_trade_result_ma10",
            "eth_trade_result_expanding",
            "unique_tokens_already_sold_ratio",
            "buy_order_size_ma10",
            "buy_order_size_expanding_avg",
            "eth_trade_result_ma10/buy_order_size_ma10",
            "profit_per_trade"
        ]]

        selected_columns.fillna(method='ffill', inplace=True)

        selected_columns.fillna(0, inplace=True)

        return selected_columns
