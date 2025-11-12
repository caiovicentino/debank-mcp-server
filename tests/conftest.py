"""Pytest configuration and shared fixtures."""

import pytest
import os
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def debank_api_key():
    """Provide a test API key."""
    return "AccessKey test_key_12345"


@pytest.fixture
def mock_env(debank_api_key, monkeypatch):
    """Set up environment variables for testing."""
    monkeypatch.setenv("DEBANK_ACCESS_KEY", debank_api_key)


@pytest.fixture
def valid_address():
    """Return a valid Ethereum address (Vitalik's)."""
    return "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"


@pytest.fixture
def invalid_address():
    """Return an invalid Ethereum address."""
    return "0xinvalid"


@pytest.fixture
def valid_chain_id():
    """Return a valid chain ID."""
    return "eth"


@pytest.fixture
def invalid_chain_id():
    """Return an invalid chain ID."""
    return "invalid_chain"


@pytest.fixture
def sample_token_id():
    """Return a sample token ID (USDC on Ethereum)."""
    return "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"


@pytest.fixture
def mock_response_chains():
    """Mock response for get_chains endpoint."""
    return [
        {
            "id": "eth",
            "name": "Ethereum",
            "native_token": {
                "id": "eth",
                "symbol": "ETH",
                "name": "Ethereum"
            },
            "logo_url": "https://..."
        },
        {
            "id": "bsc",
            "name": "BNB Chain",
            "native_token": {
                "id": "bsc",
                "symbol": "BNB",
                "name": "BNB"
            },
            "logo_url": "https://..."
        }
    ]


@pytest.fixture
def mock_response_user_balance():
    """Mock response for user balance endpoint."""
    return {
        "total_usd_value": 1234567.89,
        "chain_list": [
            {
                "id": "eth",
                "name": "Ethereum",
                "usd_value": 1000000.00
            },
            {
                "id": "bsc",
                "name": "BNB Chain",
                "usd_value": 234567.89
            }
        ]
    }


@pytest.fixture
def mock_response_user_tokens():
    """Mock response for user tokens endpoint."""
    return [
        {
            "id": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
            "chain": "eth",
            "name": "USD Coin",
            "symbol": "USDC",
            "display_symbol": "USDC",
            "decimals": 6,
            "logo_url": "https://...",
            "price": 1.00,
            "amount": 10000.0,
            "raw_amount": 10000000000,
            "balance": 10000.0
        }
    ]


@pytest.fixture
def mock_response_protocols():
    """Mock response for protocols endpoint."""
    return [
        {
            "id": "uniswap3",
            "chain": "eth",
            "name": "Uniswap V3",
            "site_url": "https://app.uniswap.org",
            "logo_url": "https://...",
            "tvl": 3500000000.0
        },
        {
            "id": "aave3",
            "chain": "eth",
            "name": "Aave V3",
            "site_url": "https://app.aave.com",
            "logo_url": "https://...",
            "tvl": 5000000000.0
        }
    ]


@pytest.fixture
def mock_response_token_info():
    """Mock response for token info endpoint."""
    return {
        "id": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
        "chain": "eth",
        "name": "USD Coin",
        "symbol": "USDC",
        "display_symbol": "USDC",
        "decimals": 6,
        "logo_url": "https://...",
        "price": 1.00,
        "is_verified": True,
        "is_core": True
    }


@pytest.fixture
def mock_response_simulate_tx():
    """Mock response for transaction simulation."""
    return {
        "pre_exec": {
            "success": True,
            "error": None
        },
        "balance_change": {
            "send_token_list": [
                {
                    "id": "eth",
                    "symbol": "ETH",
                    "amount": 1.0,
                    "usd_value": 2500.0
                }
            ],
            "receive_token_list": [
                {
                    "id": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
                    "symbol": "USDC",
                    "amount": 2480.0,
                    "usd_value": 2480.0
                }
            ]
        },
        "gas": {
            "gas_limit": 150000,
            "gas_price": 50000000000,
            "gas_used": 145000
        }
    }


@pytest.fixture
def mock_response_account_units():
    """Mock response for account units endpoint."""
    return {
        "balance": 15000,
        "stats": [
            {"usage": 245, "remains": 15000, "date": "2025-01-11"},
            {"usage": 312, "remains": 15245, "date": "2025-01-10"},
            {"usage": 189, "remains": 15557, "date": "2025-01-09"}
        ]
    }


@pytest.fixture
def sample_transaction():
    """Return a sample transaction for testing."""
    return {
        "chainId": "eth",
        "from": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        "to": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        "value": "0",
        "data": "0xa9059cbb000000000000000000000000..."
    }


@pytest.fixture
async def mock_debank_client(mocker):
    """Create a mocked DeBank client."""
    client = mocker.patch("mcp_server_debank.client.DeBankClient")
    client.return_value.get = AsyncMock()
    client.return_value.post = AsyncMock()
    return client


@pytest.fixture
def mock_httpx_response():
    """Create a mock httpx response."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"success": True}
    mock_response.raise_for_status = MagicMock()
    return mock_response
