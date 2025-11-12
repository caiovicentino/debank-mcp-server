"""
DeBank MCP Server

FastMCP server providing tools for interacting with the DeBank API.
Enables AI assistants to access DeFi portfolio data, token information,
and blockchain analytics.

Usage:
    # Run with uvx
    uvx mcp-server-debank

    # Run directly
    python -m mcp_server_debank.server

Environment Variables:
    DEBANK_ACCESS_KEY: DeBank API access key (required)
"""

import os
import sys
from typing import Optional
from fastmcp import FastMCP
from dotenv import load_dotenv

from .client import DeBankClient
from .portfolio_tools import register_portfolio_tools
from .advanced_tools import register_advanced_tools

# Load environment variables from .env file
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP(
    "DeBank API",
    dependencies=["httpx", "pydantic"]
)

# Global client instance (will be initialized on first use)
_client: Optional[DeBankClient] = None


def get_client() -> DeBankClient:
    """
    Get or create the DeBank API client instance.

    Returns:
        Initialized DeBankClient instance

    Raises:
        ValueError: If DEBANK_ACCESS_KEY environment variable is not set
    """
    global _client

    if _client is None:
        access_key = os.getenv("DEBANK_ACCESS_KEY")

        if not access_key:
            raise ValueError(
                "DEBANK_ACCESS_KEY environment variable is required. "
                "Please set it in your environment or .env file."
            )

        _client = DeBankClient(access_key=access_key)

    return _client


# ============================================================================
# REGISTER PORTFOLIO TOOLS (Agent 3)
# ============================================================================
# Portfolio & Data Tools: User tokens, NFTs, protocols, history, approvals
register_portfolio_tools(mcp, get_client)

# ============================================================================
# REGISTER ADVANCED TOOLS (Agent 4 + Agent 5)
# ============================================================================
# Advanced Analytics: Net curve, pools, transactions, gas, API usage, social
register_advanced_tools(mcp, get_client)


# ============================================================================
# CORE DEBANK API TOOLS
# ============================================================================
# Implemented by Agent 2: Core Tools Implementation
# All tools provide comprehensive error handling and detailed documentation


@mcp.tool()
async def debank_get_chains(chain_id: str = None) -> dict:
    """Get blockchain network information from DeBank.

    This tool retrieves comprehensive information about blockchain networks
    supported by DeBank, including network details, native tokens, and
    protocol counts.

    Args:
        chain_id: Optional chain ID. If provided, returns single chain info.
                 If None, returns all supported chains.
                 Examples: "eth", "bsc", "polygon", "arbitrum", "optimism"

    Returns:
        Chain object(s) with the following structure:
        {
            "id": "eth",
            "name": "Ethereum",
            "logo_url": "https://...",
            "native_token_id": "eth",
            "wrapped_token_id": "0xc02...",
            "is_support_pre_exec": true
        }

    Examples:
        - Get all chains: debank_get_chains()
        - Get Ethereum: debank_get_chains(chain_id="eth")
        - Get Binance Smart Chain: debank_get_chains(chain_id="bsc")
    """
    try:
        client = get_client()

        if chain_id:
            # Get specific chain
            result = await client.get(f"/v1/chain", params={"id": chain_id})
            return {"chain": result}
        else:
            # Get all chains
            result = await client.get("/v1/chain/list")
            return {"chains": result, "count": len(result)}

    except ValueError as e:
        return {
            "error": "Validation error",
            "message": str(e),
            "type": "validation_error"
        }
    except Exception as e:
        return {
            "error": "Unexpected error",
            "message": str(e),
            "type": "unknown_error"
        }


@mcp.tool()
async def debank_get_protocols(
    protocol_id: str = None,
    chain_id: str = None,
    all_chains: bool = False
) -> dict:
    """Get DeFi protocol information from DeBank.

    This tool retrieves comprehensive information about DeFi protocols,
    including TVL (Total Value Locked), supported chains, and protocol
    metadata.

    Args:
        protocol_id: Optional specific protocol ID (e.g., 'uniswap', 'aave',
                    'compound', 'curve', 'lido', 'makerdao')
        chain_id: Optional filter by chain (e.g., 'eth', 'bsc', 'polygon')
        all_chains: If True, get all protocols across all chains

    Returns:
        Protocol object(s) with the following structure:
        {
            "id": "uniswap",
            "name": "Uniswap",
            "chain": "eth",
            "logo_url": "https://...",
            "tvl": 5234567890,
            "portfolio_item_list": [...]
        }

    Examples:
        - Get all protocols on Ethereum: debank_get_protocols(chain_id="eth")
        - Get specific protocol: debank_get_protocols(protocol_id="uniswap")
        - Get all protocols: debank_get_protocols(all_chains=True)
        - Get Aave on Polygon: debank_get_protocols(protocol_id="aave", chain_id="polygon")
    """
    try:
        client = get_client()

        # Validate mutually exclusive parameters
        if protocol_id and all_chains:
            raise ValueError("Cannot specify both protocol_id and all_chains")

        if protocol_id:
            # Get specific protocol
            params = {"id": protocol_id}
            if chain_id:
                params["chain_id"] = chain_id
            result = await client.get("/v1/protocol", params=params)
            return {"protocol": result}
        elif all_chains:
            # Get all protocols across all chains
            result = await client.get("/v1/protocol/all_list")
            return {"protocols": result, "count": len(result) if isinstance(result, list) else 0}
        elif chain_id:
            # Get protocols on specific chain
            result = await client.get("/v1/protocol/list", params={"chain_id": chain_id})
            return {"protocols": result, "count": len(result) if isinstance(result, list) else 0}
        else:
            # Default: get all protocols
            result = await client.get("/v1/protocol/all_list")
            return {"protocols": result, "count": len(result) if isinstance(result, list) else 0}

    except ValueError as e:
        return {
            "error": "Validation error",
            "message": str(e),
            "type": "validation_error"
        }
    except Exception as e:
        return {
            "error": "Unexpected error",
            "message": str(e),
            "type": "unknown_error"
        }


@mcp.tool()
async def debank_get_token_info(
    chain_id: str,
    token_id: str = None,
    token_ids: list = None,
    date: str = None
) -> dict:
    """Get token information and prices from DeBank.

    This tool retrieves comprehensive token data including current prices,
    historical prices, decimals, symbols, logos, and verification status.

    Args:
        chain_id: Blockchain ID (required). Examples: "eth", "bsc", "polygon"
        token_id: Single token contract address (0x prefixed)
        token_ids: List of token addresses (max 100, 0x prefixed)
        date: Historical date in YYYY-MM-DD format for price lookup

    Returns:
        Token object(s) with the following structure:
        {
            "id": "0xdac17f958d2ee523a2206206994597c13d831ec7",
            "chain": "eth",
            "name": "Tether USD",
            "symbol": "USDT",
            "price": 1.0,
            "decimals": 6,
            "logo_url": "https://...",
            "is_verified": true,
            "is_core": true
        }

    Examples:
        - Get USDT: debank_get_token_info(
            chain_id="eth",
            token_id="0xdac17f958d2ee523a2206206994597c13d831ec7"
          )
        - Get multiple tokens: debank_get_token_info(
            chain_id="eth",
            token_ids=["0xdac17f958d2ee523a2206206994597c13d831ec7", "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"]
          )
        - Get historical price: debank_get_token_info(
            chain_id="eth",
            token_id="0xdac17f958d2ee523a2206206994597c13d831ec7",
            date="2024-01-15"
          )
    """
    try:
        client = get_client()

        # Validate mutually exclusive parameters
        if token_id and token_ids:
            raise ValueError("Cannot specify both token_id and token_ids")

        if not token_id and not token_ids:
            raise ValueError("Must specify either token_id or token_ids")

        if date and token_id:
            # Get historical price for single token
            result = await client.get(
                "/v1/token/history_price",
                params={"chain_id": chain_id, "id": token_id, "date": date}
            )
            return {"token": result, "historical": True, "date": date}
        elif token_ids:
            # Get multiple tokens (max 100)
            if len(token_ids) > 100:
                raise ValueError("token_ids list cannot exceed 100 addresses")

            ids_param = ",".join(token_ids)
            result = await client.get(
                "/v1/token/list_by_ids",
                params={"chain_id": chain_id, "ids": ids_param}
            )
            if isinstance(result, list):
                return {"tokens": result, "count": len(result)}
            else:
                return {"tokens": result}
        else:
            # Get single token current info
            result = await client.get(
                "/v1/token",
                params={"chain_id": chain_id, "id": token_id}
            )
            return {"token": result}

    except ValueError as e:
        return {
            "error": "Validation error",
            "message": str(e),
            "type": "validation_error"
        }
    except Exception as e:
        return {
            "error": "Unexpected error",
            "message": str(e),
            "type": "unknown_error"
        }


@mcp.tool()
async def debank_get_token_holders(
    chain_id: str,
    token_id: str,
    limit: int = 100,
    offset: int = 0
) -> dict:
    """Get top holders of a token from DeBank.

    This tool retrieves the largest holders of a specific token, useful for
    analyzing token distribution and whale activity.

    Args:
        chain_id: Blockchain ID (required). Examples: "eth", "bsc", "polygon"
        token_id: Token contract address (required, must start with 0x)
        limit: Number of holders to return (max 100, default 100)
        offset: Starting position for pagination (max 10000, default 0)

    Returns:
        Object with holder data:
        {
            "holders": [
                {
                    "address": "0x5853ed4f26a3fcea565b3fbc698bb19cdf6deb85",
                    "amount": "1234567890000000000",
                    "usd_value": 1234567.89
                },
                ...
            ],
            "total_count": 50000
        }

    Examples:
        - Get top 100 USDT holders: debank_get_token_holders(
            chain_id="eth",
            token_id="0xdac17f958d2ee523a2206206994597c13d831ec7"
          )
        - Get next 50 holders: debank_get_token_holders(
            chain_id="eth",
            token_id="0xdac17f958d2ee523a2206206994597c13d831ec7",
            limit=50,
            offset=100
          )
    """
    try:
        client = get_client()

        # Validate required parameters
        if not token_id:
            raise ValueError("token_id is required")

        if not token_id.startswith("0x"):
            raise ValueError("token_id must start with 0x")

        # Validate limit
        if limit < 1 or limit > 100:
            raise ValueError("limit must be between 1 and 100")

        # Validate offset
        if offset < 0 or offset > 10000:
            raise ValueError("offset must be between 0 and 10000")

        result = await client.get(
            "/v1/token/top_holders",
            params={
                "chain_id": chain_id,
                "id": token_id,
                "limit": limit,
                "start": offset
            }
        )

        # Wrap response if it's a list
        if isinstance(result, list):
            return {"holders": result, "count": len(result)}
        else:
            # API might return object with holders and total_count
            return result

    except ValueError as e:
        return {
            "error": "Validation error",
            "message": str(e),
            "type": "validation_error"
        }
    except Exception as e:
        return {
            "error": "Unexpected error",
            "message": str(e),
            "type": "unknown_error"
        }


@mcp.tool()
async def debank_get_user_balance(
    address: str,
    chain_id: str = None
) -> dict:
    """Get user's total balance or chain-specific balance from DeBank.

    This tool retrieves comprehensive portfolio data for a wallet address,
    including total balance across all chains or balance on a specific chain.

    Args:
        address: User's wallet address (required, must start with 0x)
        chain_id: Optional chain ID. If provided, returns balance on that chain.
                 If None, returns total balance across all chains.
                 Examples: "eth", "bsc", "polygon", "arbitrum"

    Returns:
        Balance information:
        - If chain_id is None:
          {
              "total_usd_value": 123456.78,
              "chain_list": [
                  {
                      "id": "eth",
                      "usd_value": 98765.43
                  },
                  ...
              ]
          }
        - If chain_id is specified:
          {
              "usd_value": 98765.43,
              "chain": "eth"
          }

    Examples:
        - Get total balance: debank_get_user_balance(
            address="0x5853ed4f26a3fcea565b3fbc698bb19cdf6deb85"
          )
        - Get Ethereum balance: debank_get_user_balance(
            address="0x5853ed4f26a3fcea565b3fbc698bb19cdf6deb85",
            chain_id="eth"
          )
        - Get BSC balance: debank_get_user_balance(
            address="0x5853ed4f26a3fcea565b3fbc698bb19cdf6deb85",
            chain_id="bsc"
          )
    """
    try:
        client = get_client()

        # Validate required parameters
        if not address:
            raise ValueError("address is required")

        if not address.startswith("0x"):
            raise ValueError("address must start with 0x")

        if chain_id:
            # Get balance on specific chain
            return await client.get(
                "/v1/user/chain_balance",
                params={"id": address, "chain_id": chain_id}
            )
        else:
            # Get total balance across all chains
            return await client.get("/v1/user/total_balance", params={"id": address})

    except ValueError as e:
        return {
            "error": "Validation error",
            "message": str(e),
            "type": "validation_error"
        }
    except Exception as e:
        return {
            "error": "Unexpected error",
            "message": str(e),
            "type": "unknown_error"
        }


def main():
    """
    Entry point for running the MCP server.

    This function is called when running:
    - uvx mcp-server-debank
    - python -m mcp_server_debank.server
    """
    try:
        # Verify access key is configured
        if not os.getenv("DEBANK_ACCESS_KEY"):
            print(
                "ERROR: DEBANK_ACCESS_KEY environment variable is not set.\n"
                "Please set it before running the server:\n\n"
                "  export DEBANK_ACCESS_KEY='your_key_here'\n"
                "  # or create a .env file with:\n"
                "  DEBANK_ACCESS_KEY=your_key_here\n",
                file=sys.stderr
            )
            sys.exit(1)

        # Run the MCP server
        mcp.run()

    except KeyboardInterrupt:
        print("\nShutting down DeBank MCP server...", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"ERROR: Failed to start server: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
