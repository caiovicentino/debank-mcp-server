"""Transaction Safety Demo - Agent 4 Advanced Tools

This example demonstrates the complete transaction safety workflow:
1. Check current gas prices
2. Explain what a transaction will do
3. Simulate the transaction before sending
4. Analyze safety concerns

CRITICAL: Always simulate transactions before sending real funds!
"""

import asyncio
import os
import sys

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mcp_server_debank.server import (
    debank_get_gas_prices,
    debank_simulate_transaction,
    debank_get_user_net_curve,
    debank_get_pool_info,
    DebankAPIError
)


async def demo_safe_transaction_workflow():
    """Demonstrate safe transaction preparation and simulation."""
    print("=" * 80)
    print("TRANSACTION SAFETY WORKFLOW DEMO")
    print("=" * 80)

    # Example wallet and transaction details
    sender_address = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
    recipient_address = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"  # USDC contract

    print("\nScenario: Sending ETH to USDC contract")
    print(f"Sender: {sender_address}")
    print(f"Recipient: {recipient_address}")

    # STEP 1: Check current gas prices
    print("\n" + "=" * 80)
    print("STEP 1: Check Current Gas Prices")
    print("=" * 80)

    try:
        gas_prices = await debank_get_gas_prices(chain_id="eth")

        print("\nCurrent Ethereum Gas Prices:")
        for tier in gas_prices.get("gas_tiers", []):
            level = tier["level"]
            price_gwei = tier.get("price_gwei", 0)
            print(f"  {level.capitalize()}: {price_gwei:.2f} Gwei")

        # Get normal gas price for our transaction
        normal_tier = next(
            (t for t in gas_prices["gas_tiers"] if t["level"] == "normal"),
            None
        )
        selected_gas_price = normal_tier["price"] if normal_tier else 30000000000

        print(f"\nSelected gas price: {selected_gas_price / 1e9:.2f} Gwei (normal)")

    except DebankAPIError as e:
        print(f"Error getting gas prices: {e}")
        return

    # STEP 2: Create transaction object
    print("\n" + "=" * 80)
    print("STEP 2: Prepare Transaction")
    print("=" * 80)

    transaction = {
        "chainId": "eth",
        "from": sender_address,
        "to": recipient_address,
        "value": "1000000000000000000",  # 1 ETH in wei
        "data": "0x",  # Simple transfer, no data
        "gas": 21000,
        "maxFeePerGas": selected_gas_price,
        "maxPriorityFeePerGas": 2000000000,  # 2 Gwei tip
        "nonce": 0
    }

    print("\nTransaction Details:")
    print(f"  Chain: Ethereum")
    print(f"  Value: 1 ETH")
    print(f"  Gas Limit: 21,000")
    print(f"  Max Fee: {selected_gas_price / 1e9:.2f} Gwei")

    # STEP 3: Explain the transaction
    print("\n" + "=" * 80)
    print("STEP 3: Explain Transaction (What will it do?)")
    print("=" * 80)

    try:
        explanation = await debank_simulate_transaction(
            transaction=transaction,
            explain_only=True
        )

        print("\nTransaction Explanation:")
        if "abi" in explanation:
            abi = explanation["abi"]
            print(f"  Function: {abi.get('func', 'transfer')}")
            if "params" in abi:
                print("  Parameters:")
                for param in abi["params"]:
                    print(f"    - {param.get('name')}: {param.get('value')}")

        if "actions" in explanation:
            print("\n  Actions:")
            for action in explanation["actions"]:
                print(f"    - {action}")

    except DebankAPIError as e:
        print(f"Note: {e}")
        print("(This is expected for simple transfers with no contract interaction)")

    # STEP 4: Simulate the transaction
    print("\n" + "=" * 80)
    print("STEP 4: Simulate Transaction (Will it succeed?)")
    print("=" * 80)

    try:
        simulation = await debank_simulate_transaction(transaction=transaction)

        print("\nSimulation Results:")

        # Check if transaction will succeed
        safety = simulation.get("safety_analysis", {})
        will_succeed = safety.get("will_succeed", False)
        risk_level = safety.get("risk_level", "unknown")

        print(f"\n  Status: {'✓ Will Succeed' if will_succeed else '✗ Will FAIL'}")
        print(f"  Risk Level: {risk_level.upper()}")

        # Show estimated gas
        estimated_gas = safety.get("estimated_gas", 0)
        gas_cost_eth = (estimated_gas * selected_gas_price) / 1e18
        print(f"  Estimated Gas: {estimated_gas:,} units")
        print(f"  Estimated Cost: {gas_cost_eth:.6f} ETH")

        # Show balance changes
        balance_change = simulation.get("balance_change", {})

        send_tokens = balance_change.get("send_token_list", [])
        if send_tokens:
            print("\n  You will send:")
            for token in send_tokens:
                amount = token.get("amount", 0)
                symbol = token.get("symbol", token.get("id", "Unknown"))
                amount_usd = token.get("amount_usd", 0)
                print(f"    - {amount} {symbol} (${amount_usd:.2f})")

        receive_tokens = balance_change.get("receive_token_list", [])
        if receive_tokens:
            print("\n  You will receive:")
            for token in receive_tokens:
                amount = token.get("amount", 0)
                symbol = token.get("symbol", token.get("id", "Unknown"))
                amount_usd = token.get("amount_usd", 0)
                print(f"    + {amount} {symbol} (${amount_usd:.2f})")

        # Show warnings
        warnings = safety.get("warnings", [])
        if warnings:
            print("\n  ⚠️  WARNINGS:")
            for warning in warnings:
                print(f"    - {warning}")

        # Show recommendations
        recommendations = safety.get("recommendations", [])
        if recommendations:
            print("\n  💡 RECOMMENDATIONS:")
            for rec in recommendations:
                print(f"    - {rec}")

        # Final decision
        print("\n" + "=" * 80)
        if will_succeed and risk_level in ["low", "medium"]:
            print("✓ TRANSACTION APPEARS SAFE TO SEND")
        elif will_succeed and risk_level == "high":
            print("⚠️  TRANSACTION WILL SUCCEED BUT HAS HIGH RISK - REVIEW CAREFULLY")
        else:
            print("✗ DO NOT SEND - TRANSACTION WILL FAIL OR IS CRITICAL RISK")
        print("=" * 80)

    except DebankAPIError as e:
        print(f"\nSimulation Error: {e}")
        print("\n✗ CANNOT VERIFY SAFETY - DO NOT SEND WITHOUT FURTHER INVESTIGATION")


async def demo_portfolio_tracking():
    """Demonstrate portfolio performance tracking."""
    print("\n\n" + "=" * 80)
    print("PORTFOLIO TRACKING DEMO")
    print("=" * 80)

    # Example: Vitalik's address
    address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"

    print(f"\nTracking portfolio for: {address}")

    # STEP 1: Get 24h performance across all chains
    print("\n" + "-" * 80)
    print("24-Hour Portfolio Performance (All Chains)")
    print("-" * 80)

    try:
        net_curve = await debank_get_user_net_curve(address=address)

        if net_curve.get("summary"):
            summary = net_curve["summary"]
            print(f"\nStarting Value: ${summary['start_value_usd']:,.2f}")
            print(f"Current Value: ${summary['end_value_usd']:,.2f}")
            print(f"24h Change: ${summary['change_usd']:,.2f} ({summary['change_percent']:+.2f}%)")
            print(f"Data Points: {summary['data_points']}")

            # Show trend
            if summary["change_percent"] > 0:
                print("📈 Portfolio is UP in the last 24 hours")
            elif summary["change_percent"] < 0:
                print("📉 Portfolio is DOWN in the last 24 hours")
            else:
                print("➡️  Portfolio is FLAT in the last 24 hours")

    except DebankAPIError as e:
        print(f"Error: {e}")

    # STEP 2: Get chain-specific performance
    print("\n" + "-" * 80)
    print("Ethereum Only Performance")
    print("-" * 80)

    try:
        eth_curve = await debank_get_user_net_curve(address=address, chain_id="eth")

        if eth_curve.get("summary"):
            summary = eth_curve["summary"]
            print(f"\nETH Chain Starting Value: ${summary['start_value_usd']:,.2f}")
            print(f"ETH Chain Current Value: ${summary['end_value_usd']:,.2f}")
            print(f"ETH Chain 24h Change: ${summary['change_usd']:,.2f} ({summary['change_percent']:+.2f}%)")

    except DebankAPIError as e:
        print(f"Error: {e}")


async def demo_pool_analysis():
    """Demonstrate liquidity pool analysis."""
    print("\n\n" + "=" * 80)
    print("LIQUIDITY POOL ANALYSIS DEMO")
    print("=" * 80)

    # Example: Uniswap V2 ETH-USDC pool
    pool_id = "0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc"
    chain_id = "eth"

    print(f"\nAnalyzing pool: {pool_id}")
    print(f"Chain: {chain_id}")

    try:
        pool_info = await debank_get_pool_info(pool_id=pool_id, chain_id=chain_id)

        print(f"\nPool Name: {pool_info.get('name', 'Unknown')}")
        print(f"Protocol: {pool_info.get('protocol_id', 'Unknown')}")

        if pool_info.get("summary"):
            summary = pool_info["summary"]
            print(f"\nTotal Value Locked: ${summary['total_value_locked_usd']:,.2f}")
            print(f"Total Users: {summary['total_users']:,}")
            print(f"Valuable Users: {summary['valuable_users']:,}")
            print(f"Average Deposit: ${summary['average_deposit_usd']:,.2f}")

            # Calculate metrics
            valuable_ratio = (
                (summary['valuable_users'] / summary['total_users'] * 100)
                if summary['total_users'] > 0 else 0
            )
            print(f"\nValuable User Ratio: {valuable_ratio:.1f}%")

            if valuable_ratio > 50:
                print("✓ High quality user base")
            elif valuable_ratio > 25:
                print("~ Moderate quality user base")
            else:
                print("⚠️  Lower quality user base")

    except DebankAPIError as e:
        print(f"Error: {e}")


async def main():
    """Run all demos."""
    # Check for API key
    if not os.getenv("DEBANK_API_KEY"):
        print("=" * 80)
        print("ERROR: DEBANK_API_KEY environment variable not set")
        print("=" * 80)
        print("\nTo run this demo:")
        print("1. Get your API key from https://pro.debank.com/api")
        print("2. Set it in your environment:")
        print("   export DEBANK_API_KEY='your-key-here'")
        print("\nNote: These are example calls. With a real API key, they will")
        print("make actual requests to the DeBank API.")
        print("=" * 80)
        return

    try:
        # Demo 1: Transaction Safety
        await demo_safe_transaction_workflow()

        # Demo 2: Portfolio Tracking
        await demo_portfolio_tracking()

        # Demo 3: Pool Analysis
        await demo_pool_analysis()

        print("\n\n" + "=" * 80)
        print("ALL DEMOS COMPLETED SUCCESSFULLY")
        print("=" * 80)

    except Exception as e:
        print(f"\nDemo Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
