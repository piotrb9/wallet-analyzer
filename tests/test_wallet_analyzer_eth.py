import pytest
from src.wallet_analyzer_eth import WalletAnalyzer
import pandas as pd

# Sample data for testing
OWN_WALLET_ADDRESS = '0xcecfce5556a66bf8cb1a9f3005ce5496363a88aa'
CHAIN = 'eth'


@pytest.fixture
def wallet_analyzer():
    """Fixture to create a WalletAnalyzer instance."""
    return WalletAnalyzer(OWN_WALLET_ADDRESS, CHAIN)


@pytest.fixture
def wallet_analyzer_with_data():
    """Fixture to create a WalletAnalyzer instance."""
    wallet_analyzer = WalletAnalyzer(OWN_WALLET_ADDRESS, CHAIN)

    # Load the fixtures from csv files
    wallet_analyzer.txs_df = pd.read_csv('fixtures/txs_df.csv')
    wallet_analyzer.token_trades_df = pd.read_csv('fixtures/token_trades_df.csv')
    wallet_analyzer.swap_txs_df = pd.read_csv('fixtures/swap_txs_df.csv')

    return wallet_analyzer


def test_classify_tx_eth_transfer_out(wallet_analyzer):
    from_wallet = OWN_WALLET_ADDRESS
    to_wallet = "0x3f5ce5fbfe3e9af3971dd833d26ba9b5c936f0be"
    method_id = "0x"
    value = 0.5

    assert wallet_analyzer.classify_tx(from_wallet, to_wallet, method_id, value) == "eth_transfer_out"


def test_classify_tx_eth_transfer_in(wallet_analyzer):
    from_wallet = "0x3f5ce5fbfe3e9af3971dd833d26ba9b5c936f0be"
    to_wallet = OWN_WALLET_ADDRESS
    method_id = "0x"
    value = 0.5

    assert wallet_analyzer.classify_tx(from_wallet, to_wallet, method_id, value) == "eth_transfer_in"


def test_classify_tx_approve_zero(wallet_analyzer):
    from_wallet = OWN_WALLET_ADDRESS
    to_wallet = "0x3f5ce5fbfe3e9af3971dd833d26ba9b5c936f0be"
    method_id = "0x095ea7b3"
    value = 0

    assert wallet_analyzer.classify_tx(from_wallet, to_wallet, method_id, value) == "approve"


def test_classify_tx_approve_nonzero(wallet_analyzer):
    from_wallet = OWN_WALLET_ADDRESS
    to_wallet = "0x3f5ce5fbfe3e9af3971dd833d26ba9b5c936f0be"
    method_id = "0x095ea7b3"
    value = 0.1

    assert wallet_analyzer.classify_tx(from_wallet, to_wallet, method_id, value) == "approve"


def test_classify_tx_swap_tx_zero_value(wallet_analyzer):
    from_wallet = OWN_WALLET_ADDRESS
    to_wallet = "0x3fC91A3afd70395Cd496C647d5a6CC9D4B2b7FAD".lower()
    method_id = "0x343"
    value = 0

    assert wallet_analyzer.classify_tx(from_wallet, to_wallet, method_id, value) == "swap_tx_zero_value"


def test_classify_tx_swap_tx_swap_tx_nonzero_value(wallet_analyzer):
    from_wallet = OWN_WALLET_ADDRESS
    to_wallet = "0x3fC91A3afd70395Cd496C647d5a6CC9D4B2b7FAD".lower()
    method_id = "0x343"
    value = 0.1

    assert wallet_analyzer.classify_tx(from_wallet, to_wallet, method_id, value) == "swap_tx_nonzero_value"


def test_classify_tx_other(wallet_analyzer):
    from_wallet = OWN_WALLET_ADDRESS
    to_wallet = "0x3fC91A3afd70aac3356d5a6CC9D4B2b7FAD".lower()
    method_id = "0x343"
    value = 0.1

    assert wallet_analyzer.classify_tx(from_wallet, to_wallet, method_id, value) == "other"


def test_classify_tx_other_self(wallet_analyzer):
    from_wallet = OWN_WALLET_ADDRESS
    to_wallet = OWN_WALLET_ADDRESS
    method_id = "0x343"
    value = 0.1

    assert wallet_analyzer.classify_tx(from_wallet, to_wallet, method_id, value) == "other"


def test_classify_tx_other_not_own(wallet_analyzer):
    from_wallet = "0x3fC91A3afd70aac3356d5a6CC9D4B2b7FAD".lower()
    to_wallet = "0x3fC91A3afd70aac3356d5a6CC9D4B2b7FAD".lower()
    method_id = "0x343"
    value = 0.1

    assert wallet_analyzer.classify_tx(from_wallet, to_wallet, method_id, value) == "other"


def test_classify_tx_none_value(wallet_analyzer):
    from_wallet = OWN_WALLET_ADDRESS
    to_wallet = "0x3fC91A3afd70aac3356d5a6CC9D4B2b7FAD"
    method_id = "0x"
    value = None

    with pytest.raises(TypeError):
        wallet_analyzer.classify_tx(from_wallet, to_wallet, method_id, value)


def test_classify_tx_minus_value(wallet_analyzer):
    from_wallet = OWN_WALLET_ADDRESS
    to_wallet = "0x3fC91A3afd70aac3356d5a6CC9D4B2b7FAD"
    method_id = "0x"
    value = -1.5

    with pytest.raises(ValueError):
        wallet_analyzer.classify_tx(from_wallet, to_wallet, method_id, value)


def test_load_gas_price_history(wallet_analyzer):
    gas_price_df = wallet_analyzer.load_gas_price_history('../src/data/export-AvgGasPrice.csv')

    assert gas_price_df is not None
    assert len(gas_price_df) > 0
    assert gas_price_df.columns.tolist() == ['date', 'avgGasPrice']


def test_drop_in_out_tokens(wallet_analyzer_with_data):
    len_before = len(wallet_analyzer_with_data.swap_txs_df)
    df_after = wallet_analyzer_with_data.drop_in_out_tokens(wallet_analyzer_with_data.swap_txs_df)

    assert len(df_after) < len_before
    assert df_after is not None
    assert len(df_after) > 0

