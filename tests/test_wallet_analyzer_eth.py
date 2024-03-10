import pytest
from src.wallet_analyzer_eth import WalletAnalyzer

# Sample data for testing
OWN_WALLET_ADDRESS = '0xcecfce5556a66bf8cb1a9f3005ce5496363a88aa'
CHAIN = 'eth'


@pytest.fixture
def wallet_analyzer():
    """Fixture to create a WalletAnalyzer instance."""
    return WalletAnalyzer(OWN_WALLET_ADDRESS, CHAIN)


def test_classify_tx_eth_transfer_out(wallet_analyzer):
    from_wallet = OWN_WALLET_ADDRESS
    to_wallet = "0x3f5ce5fbfe3e9af3971dd833d26ba9b5c936f0be"
    method_id = "0x"
    value = 0.5

    # Test classify_tx() with a normal transaction
    assert wallet_analyzer.classify_tx(from_wallet, to_wallet, method_id, value) == "eth_transfer_out"


def test_classify_tx_eth_transfer_in(wallet_analyzer):
    from_wallet = "0x3f5ce5fbfe3e9af3971dd833d26ba9b5c936f0be"
    to_wallet = OWN_WALLET_ADDRESS
    method_id = "0x"
    value = 0.5

    # Test classify_tx() with a normal transaction
    assert wallet_analyzer.classify_tx(from_wallet, to_wallet, method_id, value) == "eth_transfer_in"


def test_classify_tx_approve_zero(wallet_analyzer):
    from_wallet = OWN_WALLET_ADDRESS
    to_wallet = "0x3f5ce5fbfe3e9af3971dd833d26ba9b5c936f0be"
    method_id = "0x095ea7b3"
    value = 0

    # Test classify_tx() with a normal transaction
    assert wallet_analyzer.classify_tx(from_wallet, to_wallet, method_id, value) == "approve"


def test_classify_tx_approve_nonzero(wallet_analyzer):
    from_wallet = OWN_WALLET_ADDRESS
    to_wallet = "0x3f5ce5fbfe3e9af3971dd833d26ba9b5c936f0be"
    method_id = "0x095ea7b3"
    value = 0.1

    # Test classify_tx() with a normal transaction
    assert wallet_analyzer.classify_tx(from_wallet, to_wallet, method_id, value) == "approve"


def test_classify_tx_swap_tx_zero_value(wallet_analyzer):
    from_wallet = OWN_WALLET_ADDRESS
    to_wallet = "0x3fC91A3afd70395Cd496C647d5a6CC9D4B2b7FAD".lower()
    method_id = "0x343"
    value = 0

    # Test classify_tx() with a normal transaction
    assert wallet_analyzer.classify_tx(from_wallet, to_wallet, method_id, value) == "swap_tx_zero_value"


def test_classify_tx_swap_tx_swap_tx_nonzero_value(wallet_analyzer):
    from_wallet = OWN_WALLET_ADDRESS
    to_wallet = "0x3fC91A3afd70395Cd496C647d5a6CC9D4B2b7FAD".lower()
    method_id = "0x343"
    value = 0.1

    # Test classify_tx() with a normal transaction
    assert wallet_analyzer.classify_tx(from_wallet, to_wallet, method_id, value) == "swap_tx_nonzero_value"
