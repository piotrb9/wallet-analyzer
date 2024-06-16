import json
import pandas as pd


def load_transactions(file_path, limit=100):
    # Load the JSON file
    with open(file_path, 'r') as file:
        data = json.load(file)

    data = data['results']
    return data[:limit]


def get_swaps(transactions, wallet_address):
    transactions_data = []

    for txn in transactions:
        transaction_hash = txn['transactionHash']
        fees_paid = 0
        is_swap = False
        transfer_actions = []
        tokens_involved = set()
        sol_sent = 0
        sol_received = 0
        tokens_sent = 0
        tokens_received = 0
        timestamp = None
        swap_type = None

        for action in txn['data']:
            if action['action'] == 'pay_tx_fees':
                fees_paid = action['amount'] / 1000000000  # Convert fees to SOL

            if action['action'] == 'transfer':
                transfer_actions.append(action)
                if action['token']:
                    if action['token'] != "":
                        tokens_involved.add(action['token'])

                if action['token'] == "So11111111111111111111111111111111111111112":
                    # For buy orders
                    if action['source'] == wallet_address:
                        sol_sent += action['amount']/1000000000
                    elif action['destination'] == wallet_address:
                        sol_received += action['amount']/1000000000

                elif action['token'] != "":
                    # For buy orders
                    if action['destination'] == wallet_address:
                        tokens_received += action['amount']
                    elif action['source'] == wallet_address:
                        tokens_sent += action['amount']

                timestamp = action['timestamp']

        if sol_sent > 0 and sol_received == 0:
            swap_type = "buy"
        elif sol_received > 0 and sol_sent == 0:
            swap_type = "sell"

        # token_amount = tokens_sent if tokens_sent > 0 else tokens_received

        sol_amount = sol_received - sol_sent
        token_amount = tokens_received - tokens_sent

        price = (sol_amount * 1000000000) / token_amount if token_amount > 0 else None

        token_traded_1 = list(tokens_involved)[0] if len(tokens_involved) > 0 else None
        token_traded_2 = list(tokens_involved)[1] if len(tokens_involved) > 1 else None


        transactions_data.append({
            "transaction_hash": transaction_hash,
            "timestamp": timestamp,
            "is_swap": is_swap,
            "fees": fees_paid,
            "price": price,
            "token_1": token_traded_1,
            "token_2": token_traded_2,
            "sol_sent": sol_sent,
            "sol_received": sol_received,
            "sol_amount": sol_amount,
            "tokens_sent": tokens_sent,
            "tokens_received": tokens_received,
            "token_amount": token_amount,
            "swap_type": swap_type
        })

    df = pd.DataFrame(transactions_data)

    # Show the price column precisely
    pd.set_option('display.float_format', lambda x: '%.9f' % x)

    # Price column float32
    df['price'] = df['price'].astype('float32')
    return df


# Use the function to load and process the first 100 transactions with detailed information and swap type
file_path = '../temp/solana_fm_transfers.json'  # Update the file path as needed
transactions = load_transactions(file_path)

df_transactions_with_swap_type = get_swaps(transactions, wallet_address='4D168CJRDAM3SMpyh4tYCMVV2GqwehNhLvFd2ubHDhPY')

# print(df_transactions_with_swap_type.head())


class SolanaWalletAnalyzer:
    def __init__(self, wallet: str):
        self.wallet = wallet
        self.transactions = None
        self.swap_txs_df = None

    def load_transactions(self, file_path, limit=100):
        with open(file_path, 'r') as file:
            data = json.load(file)
        self.transactions = data['results'][:limit]

    def classify_tx(self, from_wallet: str, to_wallet: str, method_id: str, value: float) -> str:
        pass

    def get_swap_type(self, txn_data):
        sol_sent = 0
        sol_received = 0
        tokens_sent = 0
        tokens_received = 0
        swap_type = None
        tokens_involved = set()

        for action in txn_data:
            if action['action'] == 'pay_tx_fees':
                fees_paid = action['amount'] / 1000000000  # Convert fees to SOL

            if action['action'] == 'transfer':
                # transfer_actions.append(action)
                if action['token']:
                    if action['token'] != "":
                        tokens_involved.add(action['token'])

                if action['token'] == "So11111111111111111111111111111111111111112":
                    if action['source'] == self.wallet:
                        sol_sent += action['amount'] / 1000000000
                    elif action['destination'] == self.wallet:
                        sol_received += action['amount'] / 1000000000

                elif action['token'] != "":
                    if action['destination'] == self.wallet:
                        tokens_received += action['amount']
                    elif action['source'] == self.wallet:
                        tokens_sent += action['amount']

        if sol_sent > 0 and sol_received == 0:
            swap_type = "swap_buy"
        elif sol_received > 0 and sol_sent == 0:
            swap_type = "swap_sell"

        sol_amount = sol_received - sol_sent
        token_amount = tokens_received - tokens_sent

        return swap_type, sol_amount, token_amount, tokens_involved

    def get_data(self):
        # Load transactions data
        txs_list = []
        swap_txs_list = []

        for txn in self.transactions:

            fees_paid = 0
            is_swap = False
            swap_type = None

            swap_type, sol_amount, token_amount, tokens_involved = self.get_swap_type(txn['data'])
            price = (sol_amount * 1000000000) / token_amount if token_amount > 0 else None

            token_traded_1 = list(tokens_involved)[0] if len(tokens_involved) > 0 else None
            token_traded_2 = list(tokens_involved)[1] if len(tokens_involved) > 1 else None

            token_traded = token_traded_1 if token_traded_2 == "So11111111111111111111111111111111111111112" else token_traded_2

            # swap_txs_list.append({
            #     "transaction_hash": txn['transactionHash'],
            #     "timestamp": timestamp,
            #     "is_swap": is_swap,
            #     "fees": fees_paid,
            #     "price": price,
            #     "token_1": token_traded_1,
            #     "token_2": token_traded_2,
            #     "sol_amount": sol_amount,
            #     "token_amount": token_amount,
            #     "swap_type": swap_type
            #
            # })

            # Fill the txs_list
            txs_list.append({
                "hash": txn['transactionHash'],
                # "blockNumber": txn['blockNumber'],
                "timeStamp": txn['data'][0]['timestamp'],
                "fees": fees_paid,
                "txType": None,
                "from": None,
                "to": None,
                "value": sol_amount,
                "swapType": swap_type,
                "swapEth": abs(sol_amount),
                "tokenValue": abs(token_amount),
                "tokenName": token_traded,
                "tokenSymbol": None,
                "tokenCa": token_traded,
                "tokenDecimal": 12.0,
                "gasPrice": 1,
                "gasUsed": 1,
                "snipe": False,
            })

        self.txs_df = pd.DataFrame(txs_list)
        self.swap_txs_df = pd.DataFrame(swap_txs_list)
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
