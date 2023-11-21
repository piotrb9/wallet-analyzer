"""Analysis of a ETH wallet"""
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

    def get_swap_txs(self, drop_snipes: bool = False, include_other_swap_types: bool = False) -> pd.DataFrame:
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


if __name__ == "__main__":
    wallet_analyzer = WalletAnalyzer("0x7e5e597c3005037246f9efdb61f79d193d1d546c")
    wallet_analyzer.get_data()
    wallet_analyzer.calculate_swap_txs()
    wallet_analyzer.check_snipers()
    print("Done")
