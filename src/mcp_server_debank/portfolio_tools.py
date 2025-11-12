"""
Portfolio & Data Tools for DeBank MCP Server
Agent 3 Implementation

These tools provide access to user portfolio data, including tokens, NFTs,
DeFi protocol positions, transaction history, and approvals.
"""

from typing import Optional, Literal
from fastmcp import FastMCP

from .validators import validate_address, validate_pagination_params, validate_time_range
from .client import DeBankClient, DeBankAPIError


def register_portfolio_tools(mcp: FastMCP, get_client_func):
    """
    Register all portfolio and data tools with the MCP server.

    Args:
        mcp: FastMCP server instance
        get_client_func: Function that returns initialized DeBankClient
    """

    @mcp.tool()
    async def debank_get_user_tokens(
        address: str,
        chain_id: Optional[str] = None,
        token_id: Optional[str] = None,
        is_all: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> dict:
        """Get user's token holdings from DeBank.

        Args:
            address: User's wallet address (required)
            chain_id: Optional chain ID. If None, returns tokens across all chains
            token_id: Optional specific token to query
            is_all: Include all tokens (True) or only valuable ones (False, default)
            limit: Maximum number of tokens to return (default: 50, max: 500)
            offset: Number of tokens to skip for pagination (default: 0)

        Returns:
            Dictionary with token holdings, amounts, prices, USD values, and pagination info

        Examples:
            - All tokens across chains: debank_get_user_tokens(address="0x...")
            - Tokens on Ethereum: debank_get_user_tokens(address="0x...", chain_id="eth")
            - Specific token balance: debank_get_user_tokens(address="0x...", chain_id="eth", token_id="0xdac17...")
            - Paginated results: debank_get_user_tokens(address="0x...", limit=10, offset=0)
        """
        try:
            # Validate address
            address = validate_address(address)

            # Validate pagination parameters (max 500 for tokens)
            if limit < 1 or limit > 500:
                raise ValueError("limit must be between 1 and 500")
            if offset < 0:
                raise ValueError("offset must be >= 0")

            # Get client instance
            client = get_client_func()

            # Determine which endpoint to use
            if token_id and chain_id:
                # Single token query - no pagination needed
                endpoint = "/v1/user/token"
                params = {
                    "id": address,
                    "chain_id": chain_id,
                    "token_id": token_id
                }
            elif chain_id:
                # Tokens on specific chain
                endpoint = "/v1/user/token_list"
                params = {
                    "id": address,
                    "chain_id": chain_id,
                    "is_all": str(is_all).lower()
                }
            else:
                # All tokens across chains
                endpoint = "/v1/user/all_token_list"
                params = {
                    "id": address,
                    "is_all": str(is_all).lower()
                }

            data = await client.get(endpoint, params=params)

            # Format response with summary
            if isinstance(data, list):
                # Apply pagination by slicing the results
                total_count = len(data)
                paginated_data = data[offset:offset + limit]

                total_value = sum(token.get("amount", 0) * token.get("price", 0) for token in paginated_data)
                has_more = (offset + limit) < total_count

                return {
                    "success": True,
                    "address": address,
                    "chain_id": chain_id or "all_chains",
                    "pagination": {
                        "total_count": total_count,
                        "returned_count": len(paginated_data),
                        "limit": limit,
                        "offset": offset,
                        "has_more": has_more,
                        "next_offset": offset + limit if has_more else None
                    },
                    "total_usd_value": round(total_value, 2),
                    "tokens": paginated_data,
                    "warning": "Results were paginated. Use limit/offset to fetch more." if total_count > limit else None
                }
            else:
                # Single token response
                return {
                    "success": True,
                    "address": address,
                    "chain_id": chain_id,
                    "token_id": token_id,
                    "token": data
                }

        except DeBankAPIError as e:
            return {
                "success": False,
                "error": "API request failed",
                "details": str(e)
            }
        except Exception as e:
            return {
                "success": False,
                "error": "Request failed",
                "details": str(e)
            }

    @mcp.tool()
    async def debank_get_user_nfts(
        address: str,
        chain_id: Optional[str] = None,
        is_all: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> dict:
        """Get user's NFT holdings from DeBank.

        Args:
            address: User's wallet address (required)
            chain_id: Optional chain ID. If None, returns NFTs across all chains
            is_all: Include all NFTs (True) or only valuable ones (False, default)
            limit: Maximum number of NFTs to return (default: 50, max: 500)
            offset: Number of NFTs to skip for pagination (default: 0)

        Returns:
            Dictionary with NFTs, metadata, content URLs, attributes, valuations, and pagination info

        Examples:
            - All NFTs: debank_get_user_nfts(address="0x...")
            - NFTs on Ethereum: debank_get_user_nfts(address="0x...", chain_id="eth")
            - Paginated results: debank_get_user_nfts(address="0x...", limit=10, offset=0)
        """
        try:
            # Validate address
            address = validate_address(address)

            # Validate pagination parameters (max 500 for NFTs)
            if limit < 1 or limit > 500:
                raise ValueError("limit must be between 1 and 500")
            if offset < 0:
                raise ValueError("offset must be >= 0")

            # Get client instance
            client = get_client_func()

            # Determine which endpoint to use
            if chain_id:
                # NFTs on specific chain
                endpoint = "/v1/user/nft_list"
                params = {
                    "id": address,
                    "chain_id": chain_id,
                    "is_all": str(is_all).lower()
                }
            else:
                # All NFTs across chains
                endpoint = "/v1/user/all_nft_list"
                params = {
                    "id": address,
                    "is_all": str(is_all).lower()
                }

            data = await client.get(endpoint, params=params)

            # Format response with summary
            if isinstance(data, list):
                # Apply pagination by slicing the results
                total_count = len(data)
                paginated_data = data[offset:offset + limit]

                total_value = sum(
                    nft.get("usd_price", 0) if nft.get("usd_price") else 0
                    for nft in paginated_data
                )
                collections = set(nft.get("contract_name", "Unknown") for nft in paginated_data)
                has_more = (offset + limit) < total_count

                return {
                    "success": True,
                    "address": address,
                    "chain_id": chain_id or "all_chains",
                    "pagination": {
                        "total_count": total_count,
                        "returned_count": len(paginated_data),
                        "limit": limit,
                        "offset": offset,
                        "has_more": has_more,
                        "next_offset": offset + limit if has_more else None
                    },
                    "collection_count": len(collections),
                    "total_usd_value": round(total_value, 2),
                    "nfts": paginated_data,
                    "warning": "Results were paginated. Use limit/offset to fetch more." if total_count > limit else None
                }
            else:
                return {
                    "success": True,
                    "address": address,
                    "data": data
                }

        except DeBankAPIError as e:
            return {
                "success": False,
                "error": "API request failed",
                "details": str(e)
            }
        except Exception as e:
            return {
                "success": False,
                "error": "Request failed",
                "details": str(e)
            }

    @mcp.tool()
    async def debank_get_user_protocols(
        address: str,
        protocol_id: Optional[str] = None,
        chain_id: Optional[str] = None,
        detail_level: Literal["simple", "complex"] = "complex"
    ) -> dict:
        """Get user's DeFi protocol positions from DeBank.

        Args:
            address: User's wallet address (required)
            protocol_id: Optional specific protocol ID
            chain_id: Optional chain ID. If None, returns positions across all chains
            detail_level: "simple" for balances only, "complex" for full position details (default: "complex")

        Returns:
            Protocol positions with assets, debts, rewards, and portfolio items

        Details:
            - "simple": Returns net_usd_value, asset_usd_value, debt_usd_value per protocol
            - "complex": Returns full PortfolioItemObject with supply tokens, borrow tokens, rewards, etc.

        Examples:
            - All positions detailed: debank_get_user_protocols(address="0x...")
            - Simple balance summary: debank_get_user_protocols(address="0x...", detail_level="simple")
            - Specific protocol: debank_get_user_protocols(address="0x...", protocol_id="aave", chain_id="eth")
        """
        try:
            # Validate address
            address = validate_address(address)

            # Get client instance
            client = get_client_func()

            # Determine which endpoint to use
            if protocol_id:
                # Single protocol query
                endpoint = "/v1/user/protocol"
                params = {
                    "id": address,
                    "protocol_id": protocol_id
                }
                if chain_id:
                    params["chain_id"] = chain_id
            elif detail_level == "simple":
                # Simple protocol list
                if chain_id:
                    endpoint = "/v1/user/simple_protocol_list"
                    params = {
                        "id": address,
                        "chain_id": chain_id
                    }
                else:
                    endpoint = "/v1/user/all_simple_protocol_list"
                    params = {"id": address}
            else:
                # Complex protocol list (default)
                if chain_id:
                    endpoint = "/v1/user/complex_protocol_list"
                    params = {
                        "id": address,
                        "chain_id": chain_id
                    }
                else:
                    endpoint = "/v1/user/all_complex_protocol_list"
                    params = {"id": address}

            data = await client.get(endpoint, params=params)

            # Format response with summary
            if isinstance(data, list):
                # Multiple protocols
                total_net_value = 0
                total_asset_value = 0
                total_debt_value = 0
                protocol_count = len(data)

                for protocol in data:
                    if detail_level == "simple":
                        total_net_value += protocol.get("net_usd_value", 0)
                        total_asset_value += protocol.get("asset_usd_value", 0)
                        total_debt_value += protocol.get("debt_usd_value", 0)
                    else:
                        # Complex: calculate from portfolio_item_list
                        for item in protocol.get("portfolio_item_list", []):
                            stats = item.get("stats", {})
                            total_net_value += stats.get("net_usd_value", 0)
                            total_asset_value += stats.get("asset_usd_value", 0)
                            total_debt_value += stats.get("debt_usd_value", 0)

                return {
                    "success": True,
                    "address": address,
                    "chain_id": chain_id or "all_chains",
                    "detail_level": detail_level,
                    "protocol_count": protocol_count,
                    "summary": {
                        "total_net_usd_value": round(total_net_value, 2),
                        "total_asset_usd_value": round(total_asset_value, 2),
                        "total_debt_usd_value": round(total_debt_value, 2)
                    },
                    "protocols": data
                }
            else:
                # Single protocol response
                return {
                    "success": True,
                    "address": address,
                    "protocol_id": protocol_id,
                    "chain_id": chain_id,
                    "protocol": data
                }

        except DeBankAPIError as e:
            return {
                "success": False,
                "error": "API request failed",
                "details": str(e)
            }
        except Exception as e:
            return {
                "success": False,
                "error": "Request failed",
                "details": str(e)
            }

    @mcp.tool()
    async def debank_get_user_history(
        address: str,
        chain_id: Optional[str] = None,
        token_id: Optional[str] = None,
        start_time: Optional[int] = None,
        page_count: int = 20
    ) -> dict:
        """Get user's transaction history from DeBank.

        Args:
            address: User's wallet address (required)
            chain_id: Optional chain ID. If None, returns history across all chains
            token_id: Optional filter by specific token
            start_time: Optional Unix timestamp to start from
            page_count: Number of transactions to return (default: 20)

        Returns:
            Dictionary with:
            - history_list: Array of transaction objects
            - cate_dict: Transaction categories
            - project_dict: Involved projects/protocols
            - token_dict: Token metadata
            - cex_dict: CEX data if applicable

        Examples:
            - Recent history: debank_get_user_history(address="0x...")
            - Ethereum only: debank_get_user_history(address="0x...", chain_id="eth")
            - USDT transactions: debank_get_user_history(address="0x...", chain_id="eth", token_id="0xdac17...")
        """
        try:
            # Validate address
            address = validate_address(address)

            # Validate pagination
            _, page_count = validate_pagination_params(None, page_count, max_page_count=100)

            # Get client instance
            client = get_client_func()

            # Determine which endpoint to use
            if chain_id:
                # History on specific chain
                endpoint = "/v1/user/history_list"
                params = {
                    "id": address,
                    "chain_id": chain_id,
                    "page_count": page_count
                }
            else:
                # History across all chains
                endpoint = "/v1/user/all_history_list"
                params = {
                    "id": address,
                    "page_count": page_count
                }

            # Add optional parameters
            if token_id:
                params["token_id"] = token_id
            if start_time:
                params["start_time"] = start_time

            data = await client.get(endpoint, params=params)

            # Validate response structure
            if not isinstance(data, dict):
                return {
                    "success": False,
                    "error": "Unexpected response format",
                    "details": f"API returned {type(data).__name__} instead of dict",
                    "address": address,
                    "chain_id": chain_id or "all"
                }

            # Format response with summary
            history_list = data.get("history_list", [])
            cate_dict = data.get("cate_dict", {})
            project_dict = data.get("project_dict", {})
            token_dict = data.get("token_dict", {})
            cex_dict = data.get("cex_dict", {})

            # Calculate summary statistics
            total_tx_count = len(history_list)
            chains_involved = set(tx.get("chain_id", "unknown") for tx in history_list)

            # Calculate total value (sum of sends and receives)
            total_value_usd = 0
            for tx in history_list:
                sends = tx.get("sends", [])
                receives = tx.get("receives", [])
                for item in sends + receives:
                    # Type coercion to handle strings/nulls
                    amount = float(item.get("amount", 0) or 0)
                    price = float(item.get("price", 0) or 0)
                    total_value_usd += amount * price

            return {
                "success": True,
                "address": address,
                "chain_id": chain_id or "all_chains",
                "filters": {
                    "token_id": token_id,
                    "start_time": start_time,
                    "page_count": page_count
                },
                "summary": {
                    "transaction_count": total_tx_count,
                    "chains_involved": list(chains_involved),
                    "total_value_usd": round(total_value_usd, 2)
                },
                "history_list": history_list,
                "cate_dict": cate_dict,
                "project_dict": project_dict,
                "token_dict": token_dict,
                "cex_dict": cex_dict
            }

        except DeBankAPIError as e:
            return {
                "success": False,
                "error": "API request failed",
                "details": str(e)
            }
        except Exception as e:
            return {
                "success": False,
                "error": "Request failed",
                "details": str(e)
            }

    @mcp.tool()
    async def debank_get_user_approvals(
        address: str,
        chain_id: str,
        approval_type: Literal["token", "nft"] = "token"
    ) -> dict:
        """Get user's token/NFT approvals and authorizations from DeBank.

        Args:
            address: User's wallet address (required)
            chain_id: Blockchain ID (required)
            approval_type: "token" or "nft" (default: "token")

        Returns:
            For tokens: Array of authorized tokens with spender info and exposure values
            For NFTs: Object with tokens, contracts, and total approved amounts

        Security Note:
            This shows which contracts have permission to spend user's assets.
            High exposure values indicate security risk.

        Examples:
            - Token approvals: debank_get_user_approvals(address="0x...", chain_id="eth")
            - NFT approvals: debank_get_user_approvals(address="0x...", chain_id="eth", approval_type="nft")
        """
        try:
            # Validate address
            address = validate_address(address)

            # Validate chain_id is provided
            if not chain_id:
                return {
                    "success": False,
                    "error": "chain_id is required for approvals endpoint"
                }

            # Get client instance
            client = get_client_func()

            # Determine which endpoint to use
            if approval_type == "token":
                endpoint = "/v1/user/token_authorized_list"
            else:
                endpoint = "/v1/user/nft_authorized_list"

            params = {
                "id": address,
                "chain_id": chain_id
            }

            data = await client.get(endpoint, params=params)

            # Format response with security analysis
            if approval_type == "token":
                # Token approvals - array format
                if isinstance(data, list):
                    total_exposure = sum(
                        float(approval.get("value", 0) or 0) *
                        float(approval.get("token", {}).get("price", 0) or 0)
                        for approval in data
                    )

                    high_risk_approvals = [
                        approval for approval in data
                        if (approval.get("value", 0) * approval.get("token", {}).get("price", 0)) > 10000
                    ]

                    spenders = set(
                        approval.get("spender", {}).get("protocol", {}).get("name", "Unknown")
                        for approval in data
                    )

                    return {
                        "success": True,
                        "address": address,
                        "chain_id": chain_id,
                        "approval_type": "token",
                        "security_analysis": {
                            "total_approvals": len(data),
                            "total_exposure_usd": round(total_exposure, 2),
                            "high_risk_count": len(high_risk_approvals),
                            "unique_spenders": len(spenders),
                            "spender_list": list(spenders)
                        },
                        "approvals": data,
                        "high_risk_approvals": high_risk_approvals
                    }
                else:
                    # Non-list response - add debug info
                    return {
                        "success": True,
                        "approvals": [],
                        "count": 0,
                        "warning": "Unexpected response structure",
                        "raw_response_type": type(data).__name__,
                        "address": address,
                        "chain_id": chain_id,
                        "approval_type": "token"
                    }
            else:
                # NFT approvals - object format with tokens and contracts
                tokens = data.get("tokens", [])
                contracts = data.get("contracts", [])

                total_nft_approvals = len(tokens)
                total_contract_approvals = len(contracts)

                spenders = set()
                for token in tokens:
                    spender_name = token.get("spender", {}).get("protocol", {}).get("name", "Unknown")
                    spenders.add(spender_name)
                for contract in contracts:
                    spender_name = contract.get("spender", {}).get("protocol", {}).get("name", "Unknown")
                    spenders.add(spender_name)

                return {
                    "success": True,
                    "address": address,
                    "chain_id": chain_id,
                    "approval_type": "nft",
                    "security_analysis": {
                        "total_nft_approvals": total_nft_approvals,
                        "total_contract_approvals": total_contract_approvals,
                        "unique_spenders": len(spenders),
                        "spender_list": list(spenders)
                    },
                    "tokens": tokens,
                    "contracts": contracts
                }

        except DeBankAPIError as e:
            return {
                "success": False,
                "error": "API request failed",
                "details": str(e)
            }
        except Exception as e:
            return {
                "success": False,
                "error": "Request failed",
                "details": str(e)
            }
