"""
DeBank MCP Server Usage Examples

This file demonstrates real-world scenarios for using the DeBank MCP server
through Claude Desktop or programmatically via the MCP protocol.

These examples show common workflows for crypto portfolio analysis,
DeFi position tracking, transaction safety, and blockchain analytics.
"""

# Example addresses for demonstrations (well-known public addresses)
VITALIK_ADDRESS = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
EXAMPLE_ADDRESS = "0x5853ed4f26a3fcea565b3fbc698bb19cdf6deb85"


# =============================================================================
# EXAMPLE 1: Complete Portfolio Overview
# =============================================================================

async def example_portfolio_summary():
    """
    Get a complete portfolio overview for an address.

    Use Case: Financial advisor analyzing a client's crypto holdings
    Tools Used: debank_get_user_balance, debank_get_user_tokens,
                debank_get_user_protocols, debank_get_user_nfts
    """
    address = EXAMPLE_ADDRESS

    # Step 1: Get total portfolio value
    balance = await debank_get_user_balance(address)
    print(f"Total Portfolio Value: ${balance['total_usd_value']:,.2f}")

    # Step 2: Get all token holdings
    tokens = await debank_get_user_tokens(
        address=address,
        is_all=False  # Only tokens with balance
    )
    print(f"Tokens Held: {len(tokens)} different tokens")

    # Step 3: Get DeFi positions
    protocols = await debank_get_user_protocols(
        address=address,
        detail_level="simple"
    )
    print(f"Active DeFi Protocols: {len(protocols)}")

    # Step 4: Get NFT collections
    nfts = await debank_get_user_nfts(address)
    print(f"NFT Collections: {nfts['total']}")

    return {
        "total_value": balance["total_usd_value"],
        "chains": len(balance["chain_list"]),
        "tokens": len(tokens),
        "protocols": len(protocols),
        "nfts": nfts["total"]
    }


# =============================================================================
# EXAMPLE 2: Transaction Safety Check
# =============================================================================

async def example_transaction_safety():
    """
    Simulate a transaction before sending to check for issues.

    Use Case: User wants to swap 1 ETH for USDC on Uniswap
    Tools Used: debank_simulate_transaction, debank_explain_transaction
    """
    # Transaction to simulate (Uniswap V3 swap)
    tx = {
        "chainId": "eth",
        "from": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        "to": "0xE592427A0AEce92De3Edee1F18E0157C05861564",  # Uniswap V3 Router
        "value": "1000000000000000000",  # 1 ETH
        "data": "0x414bf389..."  # Swap function call
    }

    # Step 1: Simulate the transaction
    result = await debank_simulate_transaction(tx)

    # Step 2: Check if it will succeed
    if result["pre_exec"]["success"]:
        print("Transaction will succeed!")

        # Show what will be sent
        for token in result["balance_change"]["send_token_list"]:
            print(f"Sending: {token['amount']} {token['symbol']}")

        # Show what will be received
        for token in result["balance_change"]["receive_token_list"]:
            print(f"Receiving: {token['amount']} {token['symbol']}")

        # Show gas costs
        gas_limit = result["gas"]["gas_limit"]
        gas_price = result["gas"]["gas_price"]
        gas_cost_eth = (gas_limit * gas_price) / 1e18
        print(f"Estimated Gas: {gas_cost_eth:.6f} ETH")

    else:
        print("Transaction will FAIL!")
        print(f"Error: {result['pre_exec']['error']}")
        return False

    # Step 3: Get human-readable explanation
    explanation = await debank_explain_transaction(tx)
    print(f"\nExplanation: {explanation['desc']}")

    return True


# =============================================================================
# EXAMPLE 3: DeFi Position Analysis
# =============================================================================

async def example_defi_analysis():
    """
    Analyze a user's DeFi positions across all protocols.

    Use Case: Portfolio manager reviewing client's yield farming strategy
    Tools Used: debank_get_user_protocols, debank_get_protocol_tvl
    """
    address = EXAMPLE_ADDRESS

    # Get detailed protocol positions
    protocols = await debank_get_user_protocols(
        address=address,
        detail_level="complex"
    )

    total_defi_value = 0
    positions_by_type = {}

    for protocol in protocols:
        protocol_name = protocol["name"]
        protocol_value = protocol["asset_usd_value"]
        total_defi_value += protocol_value

        # Categorize positions
        for position in protocol.get("portfolio_item_list", []):
            position_type = position["name"]  # e.g., "Lending", "Liquidity Pool"

            if position_type not in positions_by_type:
                positions_by_type[position_type] = {
                    "count": 0,
                    "total_value": 0,
                    "protocols": []
                }

            positions_by_type[position_type]["count"] += 1
            positions_by_type[position_type]["total_value"] += position["asset_usd_value"]
            positions_by_type[position_type]["protocols"].append(protocol_name)

    # Print summary
    print(f"Total DeFi Value: ${total_defi_value:,.2f}")
    print(f"\nPosition Breakdown:")
    for pos_type, data in positions_by_type.items():
        print(f"  {pos_type}:")
        print(f"    Count: {data['count']}")
        print(f"    Value: ${data['total_value']:,.2f}")
        print(f"    Protocols: {', '.join(set(data['protocols']))}")

    return positions_by_type


# =============================================================================
# EXAMPLE 4: Historical Performance Tracking
# =============================================================================

async def example_portfolio_history():
    """
    Track portfolio performance over time.

    Use Case: Investor wants to see 30-day portfolio performance
    Tools Used: debank_get_total_balance_chart, debank_get_user_history
    """
    address = EXAMPLE_ADDRESS

    from datetime import datetime, timedelta

    # Calculate date range (last 30 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    # Get historical portfolio values
    chart_data = await debank_get_total_balance_chart(
        address=address,
        start_time=start_date.strftime("%Y-%m-%d"),
        end_time=end_date.strftime("%Y-%m-%d")
    )

    # Calculate performance metrics
    if len(chart_data) >= 2:
        start_value = chart_data[0]["total_value"]
        end_value = chart_data[-1]["total_value"]
        change = end_value - start_value
        change_percent = (change / start_value) * 100

        print(f"30-Day Performance:")
        print(f"  Start: ${start_value:,.2f}")
        print(f"  End: ${end_value:,.2f}")
        print(f"  Change: ${change:,.2f} ({change_percent:+.2f}%)")

        # Find best and worst days
        max_value = max(chart_data, key=lambda x: x["total_value"])
        min_value = min(chart_data, key=lambda x: x["total_value"])

        print(f"\n  Peak: ${max_value['total_value']:,.2f} on {max_value['timestamp']}")
        print(f"  Low: ${min_value['total_value']:,.2f} on {min_value['timestamp']}")

    # Get recent transaction history
    history = await debank_get_user_history(
        address=address,
        chain_id="eth"
    )

    print(f"\nRecent Transactions: {len(history['history_list'])}")
    for tx in history["history_list"][:5]:  # Show last 5
        print(f"  - {tx['cate_id']}: {tx.get('tx_hash', 'N/A')[:10]}...")

    return {
        "start_value": start_value if len(chart_data) >= 2 else 0,
        "end_value": end_value if len(chart_data) >= 2 else 0,
        "change_percent": change_percent if len(chart_data) >= 2 else 0
    }


# =============================================================================
# EXAMPLE 5: Token Research and Discovery
# =============================================================================

async def example_token_research():
    """
    Research a token and find its holders.

    Use Case: Researcher analyzing a new DeFi token
    Tools Used: debank_search_tokens, debank_get_token_info, debank_get_token_holders
    """
    # Step 1: Search for a token by name
    search_results = await debank_search_tokens(
        query="Uniswap",
        chain_id="eth"
    )

    if search_results:
        uni_token = search_results[0]  # First result
        print(f"Found Token: {uni_token['name']} ({uni_token['symbol']})")

        # Step 2: Get detailed information
        token_id = uni_token["id"]
        token_info = await debank_get_token_info(
            chain_id="eth",
            token_id=token_id
        )

        print(f"\nToken Details:")
        print(f"  Price: ${token_info['price']:.4f}")
        print(f"  Chain: {token_info['chain']}")
        print(f"  Symbol: {token_info['symbol']}")

        # Step 3: Find top holders
        holders = await debank_get_token_holders(
            chain_id="eth",
            token_id=token_id,
            start=0,
            limit=10
        )

        print(f"\nTop 10 Holders:")
        for i, holder in enumerate(holders, 1):
            print(f"  {i}. {holder['address'][:10]}... - {holder['amount']:,.2f} tokens")

    return search_results


# =============================================================================
# EXAMPLE 6: Multi-Chain Portfolio Analysis
# =============================================================================

async def example_multi_chain_analysis():
    """
    Analyze portfolio across multiple blockchains.

    Use Case: Institutional investor tracking cross-chain allocations
    Tools Used: debank_get_chains, debank_get_user_balance, debank_get_user_tokens
    """
    address = EXAMPLE_ADDRESS

    # Step 1: Get all supported chains
    chains = await debank_get_chains()
    print(f"Total Supported Chains: {len(chains)}")

    # Step 2: Get balance breakdown by chain
    balance = await debank_get_user_balance(address)

    # Sort chains by value
    sorted_chains = sorted(
        balance["chain_list"],
        key=lambda x: x["usd_value"],
        reverse=True
    )

    print(f"\nPortfolio Distribution:")
    for chain in sorted_chains[:10]:  # Top 10 chains
        allocation = (chain["usd_value"] / balance["total_usd_value"]) * 100
        print(f"  {chain['name']}: ${chain['usd_value']:,.2f} ({allocation:.1f}%)")

    # Step 3: Get tokens for each major chain
    major_chains = ["eth", "bsc", "matic", "arb"]
    chain_tokens = {}

    for chain_id in major_chains:
        tokens = await debank_get_user_tokens(
            address=address,
            chain_id=chain_id,
            is_all=False
        )
        chain_tokens[chain_id] = len(tokens)

    print(f"\nTokens per Chain:")
    for chain_id, count in chain_tokens.items():
        print(f"  {chain_id.upper()}: {count} tokens")

    return sorted_chains


# =============================================================================
# EXAMPLE 7: Batch Transaction Simulation
# =============================================================================

async def example_batch_simulation():
    """
    Simulate multiple transactions in one call.

    Use Case: DeFi protocol testing multiple operations
    Tools Used: debank_batch_simulate_transactions
    """
    # Multiple transactions to simulate
    transactions = [
        {
            "chainId": "eth",
            "from": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
            "to": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",  # USDC
            "value": "0",
            "data": "0xa9059cbb..."  # Transfer function
        },
        {
            "chainId": "eth",
            "from": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
            "to": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",  # Uniswap V2
            "value": "1000000000000000000",
            "data": "0x7ff36ab5..."  # Swap function
        }
    ]

    # Simulate all at once
    results = await debank_batch_simulate_transactions(transactions)

    print(f"Simulated {len(results)} transactions:")
    for i, result in enumerate(results, 1):
        success = result["pre_exec"]["success"]
        status = "SUCCESS" if success else "FAIL"
        print(f"  Transaction {i}: {status}")

        if not success:
            print(f"    Error: {result['pre_exec'].get('error', 'Unknown')}")

    return results


# =============================================================================
# EXAMPLE 8: API Usage Monitoring
# =============================================================================

async def example_monitor_api_usage():
    """
    Monitor API unit consumption and remaining balance.

    Use Case: Developer tracking API costs
    Tools Used: debank_get_account_units
    """
    # Get current units balance and usage history
    account = await debank_get_account_units()

    print(f"API Units Status:")
    print(f"  Current Balance: {account['balance']:,} units")

    # Analyze 30-day usage
    if "stats" in account:
        stats = account["stats"]
        total_used = sum(day["usage"] for day in stats)
        avg_daily = total_used / len(stats)

        print(f"\n30-Day Usage:")
        print(f"  Total Used: {total_used:,} units")
        print(f"  Average Daily: {avg_daily:.1f} units")

        # Find peak usage day
        peak_day = max(stats, key=lambda x: x["usage"])
        print(f"  Peak Day: {peak_day['date']} ({peak_day['usage']} units)")

        # Estimate days remaining
        if avg_daily > 0:
            days_remaining = account["balance"] / avg_daily
            print(f"\nEstimated Days Remaining: {days_remaining:.1f} days")

    return account


# =============================================================================
# EXAMPLE 9: Protocol TVL Tracking
# =============================================================================

async def example_protocol_tvl_tracking():
    """
    Track Total Value Locked across multiple protocols.

    Use Case: DeFi analyst comparing protocol growth
    Tools Used: debank_get_protocols, debank_get_protocol_tvl
    """
    # Get list of protocols
    protocols = await debank_get_protocols()

    # Focus on major DeFi protocols
    major_protocols = [
        "uniswap3",
        "aave3",
        "compound",
        "curve",
        "lido"
    ]

    tvl_data = []

    for protocol_id in major_protocols:
        # Get TVL for each protocol
        tvl = await debank_get_protocol_tvl(protocol_id)

        if tvl:
            tvl_data.append({
                "protocol": protocol_id,
                "tvl": tvl.get("tvl", 0)
            })

    # Sort by TVL
    tvl_data.sort(key=lambda x: x["tvl"], reverse=True)

    print("Protocol TVL Rankings:")
    for i, data in enumerate(tvl_data, 1):
        print(f"  {i}. {data['protocol'].upper()}: ${data['tvl']:,.0f}")

    return tvl_data


# =============================================================================
# EXAMPLE 10: NFT Portfolio Analysis
# =============================================================================

async def example_nft_portfolio():
    """
    Analyze NFT holdings and valuations.

    Use Case: NFT collector tracking collection value
    Tools Used: debank_get_user_nfts
    """
    address = VITALIK_ADDRESS

    # Get NFT collections
    nfts = await debank_get_user_nfts(
        address=address,
        is_all=True
    )

    print(f"NFT Portfolio Summary:")
    print(f"  Total Collections: {nfts['total']}")

    total_value = 0
    collections = []

    for nft in nfts.get("data", []):
        collection_value = nft.get("amount", 1) * nft.get("floor_price", 0)
        total_value += collection_value

        collections.append({
            "name": nft.get("name", "Unknown"),
            "amount": nft.get("amount", 0),
            "floor_price": nft.get("floor_price", 0),
            "value": collection_value
        })

    # Sort by value
    collections.sort(key=lambda x: x["value"], reverse=True)

    print(f"  Total Value: ${total_value:,.2f}")
    print(f"\nTop Collections:")
    for coll in collections[:5]:
        print(f"  - {coll['name']}: {coll['amount']} NFTs @ ${coll['floor_price']:.2f} floor")

    return collections


# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    """
    Run examples to demonstrate DeBank MCP Server capabilities.

    Note: These examples require the MCP server to be running and
    configured with a valid DeBank API key.
    """
    import asyncio

    print("=" * 80)
    print("DeBank MCP Server - Usage Examples")
    print("=" * 80)

    # Run examples
    examples = [
        ("Portfolio Summary", example_portfolio_summary),
        ("Transaction Safety", example_transaction_safety),
        ("DeFi Analysis", example_defi_analysis),
        ("Portfolio History", example_portfolio_history),
        ("Token Research", example_token_research),
        ("Multi-Chain Analysis", example_multi_chain_analysis),
        ("Batch Simulation", example_batch_simulation),
        ("API Usage Monitoring", example_monitor_api_usage),
        ("Protocol TVL Tracking", example_protocol_tvl_tracking),
        ("NFT Portfolio", example_nft_portfolio)
    ]

    async def run_all_examples():
        for name, func in examples:
            print(f"\n{'=' * 80}")
            print(f"Example: {name}")
            print(f"{'=' * 80}")
            try:
                await func()
            except Exception as e:
                print(f"Error running example: {e}")

    # asyncio.run(run_all_examples())

    print("\n" + "=" * 80)
    print("Examples complete!")
    print("=" * 80)
