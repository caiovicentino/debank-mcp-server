"""Tests for Agent 4 Advanced Analytics and Transaction Tools.

Tests the 4 advanced MCP tools:
1. debank_get_user_net_curve - Portfolio performance tracking
2. debank_get_pool_info - Liquidity pool analytics
3. debank_simulate_transaction - Transaction safety simulation
4. debank_get_gas_prices - Gas market data
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mcp_server_debank.server import (
    debank_get_user_net_curve,
    debank_get_pool_info,
    debank_simulate_transaction,
    debank_get_gas_prices,
    analyze_transaction_safety,
    DebankAPIError,
    SIMULATION_SUPPORTED_CHAINS
)


# ============================================================================
# Test: debank_get_user_net_curve
# ============================================================================

@pytest.mark.asyncio
async def test_net_curve_total_all_chains():
    """Test getting net curve for all chains."""
    mock_data = [
        [1699900000, 50000.0],
        [1699903600, 50500.0],
        [1699907200, 51000.0],
        [1699910800, 50800.0]
    ]

    with patch('mcp_server_debank.server.make_debank_request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_data

        result = await debank_get_user_net_curve(address="0x1234567890123456789012345678901234567890")

        # Verify endpoint and params
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert "/v1/user/total_net_curve" in call_args[0][0]
        assert call_args[1]["params"]["id"] == "0x1234567890123456789012345678901234567890"
        assert "chain_ids" not in call_args[1]["params"]

        # Verify result structure
        assert "data" in result
        assert "summary" in result
        assert result["summary"]["start_value_usd"] == 50000.0
        assert result["summary"]["end_value_usd"] == 50800.0
        assert result["summary"]["change_usd"] == 800.0
        assert result["summary"]["change_percent"] == 1.6
        assert result["summary"]["data_points"] == 4


@pytest.mark.asyncio
async def test_net_curve_single_chain():
    """Test getting net curve for a single chain."""
    mock_data = [
        [1699900000, 10000.0],
        [1699903600, 10500.0]
    ]

    with patch('mcp_server_debank.server.make_debank_request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_data

        result = await debank_get_user_net_curve(
            address="0x1234567890123456789012345678901234567890",
            chain_id="eth"
        )

        # Verify endpoint
        call_args = mock_request.call_args
        assert "/v1/user/chain_net_curve" in call_args[0][0]
        assert call_args[1]["params"]["chain_id"] == "eth"


@pytest.mark.asyncio
async def test_net_curve_multiple_chains():
    """Test getting net curve for specific chains."""
    mock_data = [[1699900000, 20000.0], [1699903600, 20500.0]]

    with patch('mcp_server_debank.server.make_debank_request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_data

        result = await debank_get_user_net_curve(
            address="0x1234567890123456789012345678901234567890",
            chain_ids=["eth", "bsc", "matic"]
        )

        # Verify endpoint and params
        call_args = mock_request.call_args
        assert "/v1/user/total_net_curve" in call_args[0][0]
        assert call_args[1]["params"]["chain_ids"] == "eth,bsc,matic"


@pytest.mark.asyncio
async def test_net_curve_mutually_exclusive_params():
    """Test that chain_id and chain_ids cannot both be specified."""
    with pytest.raises(DebankAPIError) as exc_info:
        await debank_get_user_net_curve(
            address="0x1234567890123456789012345678901234567890",
            chain_id="eth",
            chain_ids=["bsc"]
        )

    assert "Cannot specify both chain_id and chain_ids" in str(exc_info.value)


# ============================================================================
# Test: debank_get_pool_info
# ============================================================================

@pytest.mark.asyncio
async def test_get_pool_info_success():
    """Test getting pool information."""
    mock_pool_data = {
        "pool_id": "0xpool123",
        "chain": "eth",
        "protocol_id": "uniswap_v2",
        "contract_ids": ["0xcontract1"],
        "name": "ETH-USDC Pool",
        "stats": {
            "deposit_usd_value": 5000000.0,
            "deposit_user_count": 1000,
            "deposit_valuable_user_count": 500
        }
    }

    with patch('mcp_server_debank.server.make_debank_request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_pool_data

        result = await debank_get_pool_info(pool_id="0xpool123", chain_id="eth")

        # Verify endpoint
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert "/v1/pool" in call_args[0][0]
        assert call_args[1]["params"]["id"] == "0xpool123"
        assert call_args[1]["params"]["chain_id"] == "eth"

        # Verify enhanced summary
        assert "summary" in result
        assert result["summary"]["total_value_locked_usd"] == 5000000.0
        assert result["summary"]["total_users"] == 1000
        assert result["summary"]["valuable_users"] == 500
        assert result["summary"]["average_deposit_usd"] == 5000.0
        assert result["summary"]["protocol"] == "uniswap_v2"


# ============================================================================
# Test: debank_simulate_transaction
# ============================================================================

@pytest.mark.asyncio
async def test_simulate_transaction_success():
    """Test successful transaction simulation."""
    mock_tx = {
        "chainId": "eth",
        "from": "0xsender",
        "to": "0xrecipient",
        "value": "1000000000000000000",
        "data": "0xa9059cbb"
    }

    mock_simulation = {
        "balance_change": {
            "send_token_list": [{
                "id": "eth",
                "amount": 1.0,
                "amount_usd": 2000.0
            }],
            "receive_token_list": []
        },
        "gas": {
            "gas_used": 21000
        },
        "pre_exec": {
            "success": True
        },
        "is_multisig": False
    }

    with patch('mcp_server_debank.server.make_debank_request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_simulation

        result = await debank_simulate_transaction(transaction=mock_tx)

        # Verify POST request
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert "/v1/wallet/pre_exec_tx" in call_args[0][0]
        assert call_args[1]["method"] == "POST"
        assert call_args[1]["json_data"]["tx"] == mock_tx

        # Verify safety analysis added
        assert "safety_analysis" in result
        assert result["safety_analysis"]["will_succeed"] is True
        assert result["safety_analysis"]["estimated_gas"] == 21000


@pytest.mark.asyncio
async def test_simulate_transaction_explain_only():
    """Test transaction explanation without full simulation."""
    mock_tx = {
        "chainId": "eth",
        "from": "0xsender",
        "to": "0xcontract",
        "value": "0",
        "data": "0x095ea7b3"
    }

    mock_explanation = {
        "abi": {
            "func": "approve",
            "params": [
                {"name": "spender", "value": "0xspender"},
                {"name": "amount", "value": "115792089237316195423570985008687907853269984665640564039457584007913129639935"}
            ]
        },
        "actions": ["Approve unlimited token spending"]
    }

    with patch('mcp_server_debank.server.make_debank_request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_explanation

        result = await debank_simulate_transaction(transaction=mock_tx, explain_only=True)

        # Verify explain endpoint used
        call_args = mock_request.call_args
        assert "/v1/wallet/explain_tx" in call_args[0][0]


@pytest.mark.asyncio
async def test_simulate_transaction_missing_fields():
    """Test transaction simulation with missing required fields."""
    incomplete_tx = {
        "chainId": "eth",
        "from": "0xsender"
        # Missing: to, value, data
    }

    with pytest.raises(DebankAPIError) as exc_info:
        await debank_simulate_transaction(transaction=incomplete_tx)

    error_msg = str(exc_info.value)
    assert "missing required fields" in error_msg.lower()
    assert "to" in error_msg
    assert "value" in error_msg
    assert "data" in error_msg


@pytest.mark.asyncio
async def test_simulate_transaction_unsupported_chain():
    """Test simulation on unsupported chain."""
    mock_tx = {
        "chainId": "unsupported_chain",
        "from": "0xsender",
        "to": "0xrecipient",
        "value": "0",
        "data": "0x"
    }

    with pytest.raises(DebankAPIError) as exc_info:
        await debank_simulate_transaction(transaction=mock_tx)

    error_msg = str(exc_info.value)
    assert "does not support transaction simulation" in error_msg
    assert "unsupported_chain" in error_msg


@pytest.mark.asyncio
async def test_simulate_transaction_with_pending():
    """Test simulation with pending transactions."""
    mock_tx = {
        "chainId": "eth",
        "from": "0xsender",
        "to": "0xrecipient",
        "value": "0",
        "data": "0x"
    }

    pending_txs = [
        {
            "chainId": "eth",
            "from": "0xsender",
            "to": "0xother",
            "value": "0",
            "data": "0x"
        }
    ]

    with patch('mcp_server_debank.server.make_debank_request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = {"pre_exec": {"success": True}, "gas": {"gas_used": 21000}}

        await debank_simulate_transaction(transaction=mock_tx, pending_transactions=pending_txs)

        call_args = mock_request.call_args
        assert call_args[1]["json_data"]["pending_txs"] == pending_txs


def test_analyze_transaction_safety_success():
    """Test safety analysis for successful transaction."""
    simulation = {
        "pre_exec": {"success": True},
        "balance_change": {
            "send_token_list": [],
            "receive_token_list": []
        },
        "gas": {"gas_used": 50000},
        "is_multisig": False
    }

    analysis = analyze_transaction_safety(simulation)

    assert analysis["risk_level"] == "low"
    assert analysis["will_succeed"] is True
    assert analysis["estimated_gas"] == 50000
    assert len(analysis["warnings"]) == 0


def test_analyze_transaction_safety_failure():
    """Test safety analysis for failing transaction."""
    simulation = {
        "pre_exec": {
            "success": False,
            "error": {"msg": "Insufficient balance"}
        },
        "gas": {"gas_used": 21000}
    }

    analysis = analyze_transaction_safety(simulation)

    assert analysis["risk_level"] == "critical"
    assert analysis["will_succeed"] is False
    assert "Transaction will FAIL" in analysis["warnings"][0]
    assert any("Insufficient balance" in w for w in analysis["warnings"])


def test_analyze_transaction_safety_large_transfer():
    """Test safety analysis for large value transfer."""
    simulation = {
        "pre_exec": {"success": True},
        "balance_change": {
            "send_token_list": [
                {"amount_usd": 15000.0}
            ],
            "receive_token_list": []
        },
        "gas": {"gas_used": 21000}
    }

    analysis = analyze_transaction_safety(simulation)

    assert analysis["risk_level"] == "high"
    assert any("Large token transfer" in w for w in analysis["warnings"])


def test_analyze_transaction_safety_nft_transfer():
    """Test safety analysis for NFT transfer."""
    simulation = {
        "pre_exec": {"success": True},
        "balance_change": {
            "send_token_list": [],
            "receive_token_list": [],
            "send_nft_list": [{"id": "nft1"}, {"id": "nft2"}]
        },
        "gas": {"gas_used": 100000}
    }

    analysis = analyze_transaction_safety(simulation)

    assert any("NFT" in w for w in analysis["warnings"])


def test_analyze_transaction_safety_high_gas():
    """Test safety analysis for high gas usage."""
    simulation = {
        "pre_exec": {"success": True},
        "balance_change": {
            "send_token_list": [],
            "receive_token_list": []
        },
        "gas": {"gas_used": 600000}
    }

    analysis = analyze_transaction_safety(simulation)

    assert any("High gas usage" in w for w in analysis["warnings"])


# ============================================================================
# Test: debank_get_gas_prices
# ============================================================================

@pytest.mark.asyncio
async def test_get_gas_prices_success():
    """Test getting gas prices."""
    mock_gas_data = [
        {"level": "slow", "price": 25000000000},
        {"level": "normal", "price": 30000000000},
        {"level": "fast", "price": 35000000000}
    ]

    with patch('mcp_server_debank.server.make_debank_request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_gas_data

        result = await debank_get_gas_prices(chain_id="eth")

        # Verify endpoint
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert "/v1/wallet/gas_market" in call_args[0][0]
        assert call_args[1]["params"]["chain_id"] == "eth"

        # Verify enhanced response
        assert "gas_tiers" in result
        assert "estimates" in result

        # Verify gwei conversion
        for tier in result["gas_tiers"]:
            assert "price_gwei" in tier
            if tier["level"] == "normal":
                assert tier["price_gwei"] == 30.0

        # Verify estimates
        assert "simple_transfer" in result["estimates"]
        assert result["estimates"]["simple_transfer"]["gas_units"] == 21000


@pytest.mark.asyncio
async def test_get_gas_prices_multiple_chains():
    """Test getting gas prices for different chains."""
    chains_to_test = ["eth", "bsc", "matic", "avax"]

    for chain in chains_to_test:
        with patch('mcp_server_debank.server.make_debank_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = [{"level": "normal", "price": 20000000000}]

            result = await debank_get_gas_prices(chain_id=chain)

            call_args = mock_request.call_args
            assert call_args[1]["params"]["chain_id"] == chain


# ============================================================================
# Integration Test: Full Transaction Safety Workflow
# ============================================================================

@pytest.mark.asyncio
async def test_full_transaction_safety_workflow():
    """Test complete workflow: simulate transaction and check gas prices."""
    # Step 1: Check gas prices
    mock_gas_data = [
        {"level": "slow", "price": 20000000000},
        {"level": "normal", "price": 25000000000},
        {"level": "fast", "price": 30000000000}
    ]

    # Step 2: Simulate transaction
    mock_tx = {
        "chainId": "eth",
        "from": "0xsender",
        "to": "0xrecipient",
        "value": "1000000000000000000",
        "data": "0x",
        "maxFeePerGas": 25000000000  # Using normal gas price
    }

    mock_simulation = {
        "pre_exec": {"success": True},
        "balance_change": {
            "send_token_list": [{"amount_usd": 2000.0}],
            "receive_token_list": []
        },
        "gas": {"gas_used": 21000}
    }

    with patch('mcp_server_debank.server.make_debank_request', new_callable=AsyncMock) as mock_request:
        # First call: gas prices
        mock_request.return_value = mock_gas_data
        gas_result = await debank_get_gas_prices(chain_id="eth")

        # Verify user would use normal gas price
        normal_gas = next(t for t in gas_result["gas_tiers"] if t["level"] == "normal")
        assert mock_tx["maxFeePerGas"] == normal_gas["price"]

        # Second call: simulate transaction
        mock_request.return_value = mock_simulation
        sim_result = await debank_simulate_transaction(transaction=mock_tx)

        # Verify transaction is safe
        assert sim_result["safety_analysis"]["will_succeed"] is True
        assert sim_result["safety_analysis"]["risk_level"] in ["low", "medium"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
