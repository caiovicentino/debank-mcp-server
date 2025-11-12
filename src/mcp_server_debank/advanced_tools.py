"""
Agent 4/5: Advanced Analytics and Transaction Tools for DeBank MCP Server

This module provides advanced tools for:
1. Portfolio performance tracking (24h net curve)
2. Liquidity pool analytics
3. Transaction simulation and safety analysis
4. Gas price market data
5. API usage monitoring (Agent 5)
6. Social features placeholder (Agent 5)

All tools integrate with the main FastMCP server instance.
"""

from typing import Optional, Callable
from .client import DeBankClient


# Supported chains for transaction simulation
SIMULATION_SUPPORTED_CHAINS = {
    "eth", "bsc", "matic", "avax", "boba", "op", "hmy", "ftm",
    "cro", "xdai", "mobm", "movr", "metis", "astar", "sdn", "nova"
}


async def debank_get_user_net_curve(
    client: DeBankClient,
    address: str,
    chain_id: Optional[str] = None,
    chain_ids: Optional[str] = None
) -> dict:
    """Get user's 24-hour asset value trends from DeBank.

    Args:
        client: DeBankClient instance
        address: User's wallet address (required, must start with 0x)
        chain_id: Optional single chain ID for chain-specific curve
        chain_ids: Optional comma-separated chain IDs for multi-chain aggregate

    Returns:
        Time series data with summary statistics
    """
    # Validate address
    if not address or not address.startswith("0x"):
        raise ValueError("address is required and must start with 0x")

    # Validate mutually exclusive parameters
    if chain_id and chain_ids:
        raise ValueError("Cannot specify both chain_id and chain_ids")

    # Get net curve data
    if chain_id:
        result = await client.get_user_chain_net_curve(
            user_addr=address,
            chain_id=chain_id
        )
    elif chain_ids:
        result = await client.get_user_total_net_curve(
            user_addr=address,
            chain_ids=chain_ids
        )
    else:
        result = await client.get_user_total_net_curve(user_addr=address)

    # Add metadata to help interpret the results
    if isinstance(result, list) and len(result) > 0:
        # API returns list of dicts with timestamp and usd_value
        first_value = result[0].get('usd_value', 0) if isinstance(result[0], dict) else 0
        last_value = result[-1].get('usd_value', 0) if isinstance(result[-1], dict) else 0
        change = last_value - first_value
        change_pct = (change / first_value * 100) if first_value > 0 else 0

        return {
            "success": True,
            "address": address,
            "chain_id": chain_id or "all_chains",
            "data_points": result,
            "count": len(result),
            "summary": {
                "start_value_usd": first_value,
                "end_value_usd": last_value,
                "change_usd": change,
                "change_percent": round(change_pct, 2),
                "trend": "up" if change > 0 else "down" if change < 0 else "flat"
            }
        }

    # Ensure we always return a dict
    return {
        "success": True,
        "address": address,
        "chain_id": chain_id or "all_chains",
        "data_points": result if isinstance(result, list) else [],
        "count": len(result) if isinstance(result, list) else 0,
        "summary": None
    }


async def debank_get_pool_info(
    client: DeBankClient,
    pool_id: str,
    chain_id: str
) -> dict:
    """Get liquidity pool information from DeBank.

    Args:
        client: DeBankClient instance
        pool_id: Pool identifier/contract address (required, must start with 0x)
        chain_id: Blockchain ID (required)

    Returns:
        Pool object with enhanced summary metrics
    """
    # Validate required parameters
    if not pool_id or not pool_id.startswith("0x"):
        raise ValueError("pool_id is required and must start with 0x")

    result = await client.get_pool(pool_id=pool_id, chain_id=chain_id)

    # Ensure we return a dict
    if not isinstance(result, dict):
        result = {"pool": result}

    # Add enhanced summary for easier interpretation
    if result and "stats" in result:
        stats = result["stats"]
        avg_deposit = (
            stats.get("deposit_usd_value", 0) / stats.get("deposit_user_count", 1)
            if stats.get("deposit_user_count", 0) > 0 else 0
        )

        valuable_ratio = (
            (stats.get("deposit_valuable_user_count", 0) / stats.get("deposit_user_count", 1) * 100)
            if stats.get("deposit_user_count", 0) > 0 else 0
        )

        result["summary"] = {
            "total_value_locked_usd": stats.get("deposit_usd_value", 0),
            "total_users": stats.get("deposit_user_count", 0),
            "valuable_users": stats.get("deposit_valuable_user_count", 0),
            "average_deposit_usd": round(avg_deposit, 2),
            "valuable_user_ratio_pct": round(valuable_ratio, 2),
            "protocol": result.get("protocol_id", "unknown"),
            "pool_name": result.get("name", "unknown")
        }

    return result


async def debank_simulate_transaction(
    client: DeBankClient,
    transaction_data: dict,
    pending_transactions: Optional[list] = None,
    explain_only: bool = False
) -> dict:
    """Pre-execute and explain a transaction using DeBank's simulation.

    CRITICAL SAFETY TOOL: Always simulate transactions before sending.

    Args:
        client: DeBankClient instance
        transaction_data: Transaction object with required fields
        pending_transactions: Optional array of transactions to simulate first
        explain_only: If True, only explain the transaction without full simulation

    Returns:
        Simulation results with safety analysis
    """
    # Validate required transaction fields
    required_fields = ["chainId", "from", "to", "value", "data"]
    missing_fields = [f for f in required_fields if f not in transaction_data]

    if missing_fields:
        raise ValueError(
            f"Transaction missing required fields: {', '.join(missing_fields)}. "
            f"Required: chainId, from, to, value, data"
        )

    # Validate addresses
    if not transaction_data["from"].startswith("0x"):
        raise ValueError("transaction 'from' address must start with 0x")

    if not transaction_data["to"].startswith("0x"):
        raise ValueError("transaction 'to' address must start with 0x")

    # Check if chain supports simulation
    chain_id = transaction_data["chainId"]
    if chain_id not in SIMULATION_SUPPORTED_CHAINS:
        return {
            "error": "unsupported_chain",
            "message": (
                f"Chain '{chain_id}' does not support transaction simulation. "
                f"Supported chains: {', '.join(sorted(SIMULATION_SUPPORTED_CHAINS))}"
            ),
            "supported_chains": sorted(SIMULATION_SUPPORTED_CHAINS),
            "transaction": transaction_data
        }

    # Try to execute simulation or explanation
    try:
        if explain_only:
            result = await client.explain_tx(
                tx=transaction_data,
                pending_txs=pending_transactions
            )
        else:
            result = await client.pre_exec_tx(
                tx=transaction_data,
                pending_txs=pending_transactions
            )

            # Add safety analysis for full simulations
            if result and isinstance(result, dict):
                result["safety_analysis"] = _analyze_transaction_safety(result)

        # Ensure we return a dict
        if not isinstance(result, dict):
            result = {"data": result}

        return result

    except Exception as e:
        # Return informative error for transaction simulation failures
        return {
            "error": "simulation_failed",
            "message": str(e),
            "transaction": transaction_data,
            "note": (
                "DeBank transaction simulation API has specific format requirements. "
                "This feature may require direct interaction with DeBank's web interface "
                "or a more specialized transaction simulation service."
            ),
            "alternatives": [
                "Use Tenderly or Blocknative for transaction simulation",
                "Test transactions on testnets before mainnet",
                "Use read-only calls for view/pure functions",
                "Check gas estimation with eth_estimateGas"
            ]
        }


def _analyze_transaction_safety(simulation_result: dict) -> dict:
    """Analyze simulation results for safety concerns.

    Args:
        simulation_result: Result from pre_exec_tx endpoint

    Returns:
        Safety analysis with warnings and recommendations
    """
    warnings = []
    recommendations = []
    risk_level = "low"

    # Check execution status
    pre_exec = simulation_result.get("pre_exec", {})
    if not pre_exec.get("success", True):
        warnings.append("Transaction will FAIL if executed")
        risk_level = "critical"
        error = pre_exec.get("error", {})
        if error:
            warnings.append(f"Error: {error.get('msg', 'Unknown error')}")

    # Check balance changes
    balance_change = simulation_result.get("balance_change", {})

    # Analyze token sends
    send_token_list = balance_change.get("send_token_list", [])
    if send_token_list:
        total_sent_usd = sum(token.get("amount_usd", 0) for token in send_token_list)
        if total_sent_usd > 10000:
            warnings.append(f"Large token transfer: ${total_sent_usd:,.2f}")
            risk_level = "high" if risk_level != "critical" else risk_level

    # Analyze NFT sends
    send_nft_list = balance_change.get("send_nft_list", [])
    if send_nft_list:
        warnings.append(f"Transferring {len(send_nft_list)} NFT(s)")

    # Check for approvals (common in malicious contracts)
    receive_token_list = balance_change.get("receive_token_list", [])
    if not receive_token_list and (send_token_list or send_nft_list):
        warnings.append("Sending assets but receiving nothing - verify this is intentional")
        risk_level = "medium" if risk_level == "low" else risk_level

    # Gas estimation
    gas = simulation_result.get("gas", {})
    gas_used = gas.get("gas_used", 0)
    if gas_used > 500000:
        warnings.append(f"High gas usage: {gas_used:,} units")

    # Multisig check
    if simulation_result.get("is_multisig"):
        recommendations.append("This is a multisig transaction requiring multiple signatures")

    # General recommendations
    if risk_level in ["medium", "high", "critical"]:
        recommendations.append("Review transaction details carefully before proceeding")

    if send_token_list or send_nft_list:
        recommendations.append("Verify recipient address is correct")

    return {
        "risk_level": risk_level,
        "warnings": warnings,
        "recommendations": recommendations,
        "will_succeed": pre_exec.get("success", True),
        "estimated_gas": gas_used
    }


async def debank_get_gas_prices(
    client: DeBankClient,
    chain_id: str
) -> dict:
    """Get current gas prices for a blockchain from DeBank.

    Args:
        client: DeBankClient instance
        chain_id: Blockchain ID (required)

    Returns:
        Gas price tiers with enhanced formatting and cost estimates
    """
    result = await client.get_gas_market(chain_id=chain_id)

    # Add human-readable gas prices (convert wei to gwei)
    if isinstance(result, list):
        for tier in result:
            if "price" in tier:
                tier["price_gwei"] = tier["price"] / 1_000_000_000

        # Calculate cost estimates for common transaction types
        estimates = {
            "simple_transfer": {
                "gas_units": 21000,
                "description": "Simple ETH/native token transfer"
            },
            "token_transfer": {
                "gas_units": 65000,
                "description": "ERC-20 token transfer"
            },
            "swap": {
                "gas_units": 150000,
                "description": "Token swap on DEX"
            },
            "note": "Multiply gas_units by price_gwei and divide by 1B to get cost in native token"
        }

        return {
            "success": True,
            "gas_tiers": result,
            "estimates": estimates,
            "chain": chain_id
        }

    # Ensure we return a dict
    if not isinstance(result, dict):
        return {
            "success": True,
            "gas_data": result,
            "chain": chain_id
        }

    return result


async def debank_get_account_units(client: DeBankClient) -> dict:
    """Check API units balance and 30-day usage from DeBank.

    This tool helps you monitor your API consumption and plan your usage.

    Args:
        client: DeBankClient instance

    Returns:
        balance: Remaining units (integer)
        stats: Array of 30 days usage history with usage, remains, date

    Use Cases:
        - Monitor API consumption
        - Track usage patterns
        - Plan unit purchases
        - Budget API calls
        - Set up usage alerts

    Example Response:
        {
            "balance": 15000,
            "stats": [
                {"usage": 245, "remains": 15000, "date": "2025-01-11"},
                {"usage": 312, "remains": 15245, "date": "2025-01-10"},
                ...
            ],
            "usage_analysis": {
                "total_30day_usage": 8542,
                "avg_daily_usage": 284.7,
                "days_remaining_at_current_rate": 52.7,
                "peak_day": {"date": "2025-01-05", "usage": 891}
            }
        }
    """
    result = await client.get("/v1/account/units")

    # Ensure we return a dict
    if not isinstance(result, dict):
        result = {"data": result}

    # Add usage analysis if stats are available
    if result and "stats" in result and len(result["stats"]) > 0:
        stats = result["stats"]
        total_usage = sum(day.get("usage", 0) for day in stats)
        avg_daily = total_usage / len(stats) if len(stats) > 0 else 0

        # Find peak usage day
        peak_day = max(stats, key=lambda x: x.get("usage", 0))

        # Estimate days remaining at current rate
        balance = result.get("balance", 0)
        days_remaining = balance / avg_daily if avg_daily > 0 else float('inf')

        result["usage_analysis"] = {
            "total_30day_usage": total_usage,
            "avg_daily_usage": round(avg_daily, 1),
            "days_remaining_at_current_rate": round(days_remaining, 1) if days_remaining != float('inf') else "unlimited",
            "peak_day": {
                "date": peak_day.get("date", "unknown"),
                "usage": peak_day.get("usage", 0)
            },
            "recommendation": _get_usage_recommendation(balance, avg_daily)
        }

    return result


def _get_usage_recommendation(balance: int, avg_daily_usage: float) -> str:
    """Generate usage recommendation based on balance and consumption rate.

    Args:
        balance: Current units balance
        avg_daily_usage: Average daily usage

    Returns:
        Recommendation message
    """
    if avg_daily_usage == 0:
        return "No recent usage detected. Your balance is stable."

    days_remaining = balance / avg_daily_usage

    if days_remaining < 7:
        return f"WARNING: Only {days_remaining:.1f} days of usage remaining at current rate. Consider purchasing more units."
    elif days_remaining < 14:
        return f"CAUTION: {days_remaining:.1f} days of usage remaining. Monitor your consumption closely."
    elif days_remaining < 30:
        return f"GOOD: {days_remaining:.1f} days of usage remaining. Your balance is adequate."
    else:
        return f"EXCELLENT: {days_remaining:.1f} days of usage remaining. Your balance is healthy."


async def debank_get_user_social(
    client: DeBankClient,
    access_token: str,
    social_type: str = "profile",
    limit: int = 20,
    offset: int = 0
) -> dict:
    """Get DeBank Connect social data (OAuth required - not yet implemented).

    IMPORTANT: This tool requires OAuth implementation which is not yet available.
    It will return an error message directing you to use API Pro endpoints instead.

    Args:
        client: DeBankClient instance
        access_token: OAuth bearer token (required)
        social_type: Type of social data - "profile", "followers", or "following"
        limit: Results per page (max 100, default 20)
        offset: Starting position (default 0)

    Returns:
        User profile or social connections

    Note:
        This tool requires OAuth implementation which is not yet available.
        Will return an error message directing users to use API Pro endpoints instead.

    Future Implementation:
        When OAuth is implemented, this tool will support:
        - Getting user profile information
        - Fetching follower lists
        - Retrieving following lists
        - Social network analysis

    Alternative Tools:
        Until OAuth is available, use these tools for blockchain data:
        - debank_get_user_balance: Portfolio value
        - debank_get_user_tokens: Token holdings
        - debank_get_user_protocols: DeFi positions
        - debank_get_user_nfts: NFT collections
    """
    # Return helpful error message
    return {
        "error": "OAuth not implemented",
        "message": (
            "DeBank Connect social features require OAuth authentication which is not yet supported. "
            "Use API Pro endpoints for blockchain data instead."
        ),
        "status": "not_implemented",
        "available_alternatives": [
            {
                "tool": "debank_get_user_balance",
                "description": "Get total portfolio value across all chains"
            },
            {
                "tool": "debank_get_user_tokens",
                "description": "List all tokens held by an address"
            },
            {
                "tool": "debank_get_user_protocols",
                "description": "View DeFi positions (lending, staking, LP, etc.)"
            },
            {
                "tool": "debank_get_user_nfts",
                "description": "Get NFT collections and holdings"
            }
        ],
        "future_support": {
            "planned": True,
            "features": [
                "User profile retrieval",
                "Follower list access",
                "Following list access",
                "Social network analysis"
            ],
            "requirements": [
                "OAuth 2.0 implementation",
                "DeBank Connect API access",
                "User authorization flow"
            ]
        }
    }


def register_advanced_tools(mcp, get_client: Callable):
    """Register all advanced tools with the FastMCP instance.

    This function registers tools 12-16:
    - Tool 12: debank_get_user_net_curve (24h portfolio tracking)
    - Tool 13: debank_get_pool_info (liquidity pool analytics)
    - Tool 14: debank_simulate_transaction (transaction safety)
    - Tool 15: debank_get_account_units (API usage monitoring)
    - Tool 16: debank_get_user_social (social features placeholder)

    Args:
        mcp: FastMCP server instance
        get_client: Function to get DeBankClient instance
    """

    @mcp.tool()
    async def debank_get_user_net_curve_tool(
        address: str,
        chain_id: Optional[str] = None,
        chain_ids: Optional[str] = None
    ) -> dict:
        """Get user's 24-hour asset value trends from DeBank.

        Track portfolio performance over the last 24 hours with time-series data.

        Args:
            address: User's wallet address (required, must start with 0x)
            chain_id: Optional single chain ID for chain-specific curve
            chain_ids: Optional comma-separated chain IDs for multi-chain aggregate

        Returns:
            Time series data with summary statistics including start/end values,
            change amount, change percentage, and trend direction
        """
        client = get_client()
        return await debank_get_user_net_curve(client, address, chain_id, chain_ids)

    @mcp.tool()
    async def debank_get_pool_info_tool(
        pool_id: str,
        chain_id: str
    ) -> dict:
        """Get liquidity pool information from DeBank.

        Analyze liquidity pool metrics including TVL, user counts, and statistics.

        Args:
            pool_id: Pool identifier/contract address (required, must start with 0x)
            chain_id: Blockchain ID (required)

        Returns:
            Pool object with enhanced summary metrics including TVL, user counts,
            average deposit size, and valuable user ratio
        """
        client = get_client()
        return await debank_get_pool_info(client, pool_id, chain_id)

    @mcp.tool()
    async def debank_simulate_transaction_tool(
        transaction_data: dict,
        pending_transactions: Optional[list] = None,
        explain_only: bool = False
    ) -> dict:
        """Pre-execute and explain a transaction using DeBank's simulation.

        CRITICAL SAFETY TOOL: Always simulate transactions before sending to
        avoid costly mistakes and security issues.

        Args:
            transaction_data: Transaction object with required fields (chainId, from, to, value, data)
            pending_transactions: Optional array of transactions to simulate first
            explain_only: If True, only explain the transaction without full simulation

        Returns:
            Simulation results with safety analysis including risk level, warnings,
            recommendations, and estimated gas costs
        """
        client = get_client()
        return await debank_simulate_transaction(client, transaction_data, pending_transactions, explain_only)

    @mcp.tool()
    async def debank_get_gas_prices_tool(chain_id: str) -> dict:
        """Get current gas prices for a blockchain from DeBank.

        Monitor gas prices to optimize transaction timing and costs.

        Args:
            chain_id: Blockchain ID (required)

        Returns:
            Gas price tiers (slow, normal, fast, instant) with cost estimates
            for common transaction types
        """
        client = get_client()
        return await debank_get_gas_prices(client, chain_id)

    @mcp.tool()
    async def debank_get_account_units_tool() -> dict:
        """Check API units balance and 30-day usage from DeBank.

        Monitor your API consumption to plan usage and avoid running out of units.

        Returns:
            balance: Remaining units (integer)
            stats: Array of 30 days usage history
            usage_analysis: Summary with total usage, daily average, days remaining,
                            peak usage day, and recommendations
        """
        client = get_client()
        return await debank_get_account_units(client)

    @mcp.tool()
    async def debank_get_user_social_tool(
        access_token: str,
        social_type: str = "profile",
        limit: int = 20,
        offset: int = 0
    ) -> dict:
        """Get DeBank Connect social data (OAuth required - not yet implemented).

        IMPORTANT: This tool requires OAuth implementation which is not yet available.

        Args:
            access_token: OAuth bearer token (required)
            social_type: Type of social data - "profile", "followers", or "following"
            limit: Results per page (max 100, default 20)
            offset: Starting position (default 0)

        Returns:
            Error message with list of available alternatives and future support details
        """
        client = get_client()
        return await debank_get_user_social(client, access_token, social_type, limit, offset)
