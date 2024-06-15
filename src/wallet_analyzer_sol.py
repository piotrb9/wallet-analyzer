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
        print(price)

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

print(df_transactions_with_swap_type.head())
