import pytest
from unittest.mock import patch, MagicMock
from src.download_wallet_txs import DataDownloader


def test_data_downloader_initialization():
    address = "0xdEcfCe6476A66BF8Cb1a9f3005ce5496363A99de"
    endpoint = "etherscan.com"
    startblock = 0

    downloader = DataDownloader(address, endpoint, startblock)

    assert downloader.address == address
    assert downloader.endpoint == endpoint
    assert downloader.startblock == startblock


@patch('download_wallet_txs.requests.request')
def test_get_txs_success(mock_request):
    # Setup
    mock_response = MagicMock()
    mock_response.json.return_value = {'result': ['tx1', 'tx2']}
    mock_request.return_value = mock_response

    downloader = DataDownloader("0x12345")

    # Act
    txs = downloader.get_txs()

    # Assert
    assert txs == ['tx1', 'tx2']


@patch('download_wallet_txs.requests.request')
def test_get_txs_empty_response(mock_request):
    # Setup
    mock_response = MagicMock()
    mock_response.json.return_value = {'result': None}
    mock_request.return_value = mock_response

    downloader = DataDownloader("0x12345")

    # Act
    txs = downloader.get_txs()

    # Assert
    assert txs == []


