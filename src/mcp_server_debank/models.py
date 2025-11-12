"""
Pydantic models for DeBank API responses.

Defines data models for common API response types including
chains, tokens, protocols, NFTs, and portfolio data.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl


class ChainModel(BaseModel):
    """Blockchain network information"""

    id: str = Field(..., description="Chain identifier (e.g., 'eth', 'bsc')")
    community_id: int = Field(..., description="Community chain ID")
    name: str = Field(..., description="Human-readable chain name")
    logo_url: str = Field(..., description="URL to chain logo image")
    native_token_id: str = Field(..., description="Native token identifier")
    wrapped_token_id: str = Field(..., description="Wrapped native token identifier")
    is_support_pre_exec: bool = Field(..., description="Whether pre-execution is supported")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "eth",
                "community_id": 1,
                "name": "Ethereum",
                "logo_url": "https://static.debank.com/image/chain/logo_url/eth/42ba589cd077e7bdd97db6480b0ff61d.png",
                "native_token_id": "eth",
                "wrapped_token_id": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
                "is_support_pre_exec": True
            }
        }


class TokenModel(BaseModel):
    """Token information"""

    id: str = Field(..., description="Unique token identifier")
    chain: str = Field(..., description="Chain where token exists")
    name: str = Field(..., description="Token name")
    symbol: str = Field(..., description="Token symbol/ticker")
    decimals: int = Field(..., description="Token decimal places")
    price: float = Field(..., description="Current USD price")
    logo_url: Optional[str] = Field(None, description="URL to token logo")
    is_verified: bool = Field(..., description="Whether token is verified")
    is_core: bool = Field(..., description="Whether token is a core token")
    is_wallet: bool = Field(..., description="Whether token is in wallet")
    time_at: Optional[int] = Field(None, description="Token creation timestamp")
    amount: Optional[float] = Field(None, description="Token amount held")
    raw_amount: Optional[int] = Field(None, description="Raw token amount (with decimals)")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
                "chain": "eth",
                "name": "USD Coin",
                "symbol": "USDC",
                "decimals": 6,
                "price": 1.0,
                "logo_url": "https://static.debank.com/image/eth_token/logo_url/0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48/fffcd27b9efff5a86ab942084c05924d.png",
                "is_verified": True,
                "is_core": True,
                "is_wallet": True,
                "amount": 1000.0,
                "raw_amount": 1000000000
            }
        }


class ProtocolModel(BaseModel):
    """DeFi protocol information"""

    id: str = Field(..., description="Protocol identifier")
    chain: str = Field(..., description="Chain where protocol operates")
    name: str = Field(..., description="Protocol name")
    site_url: Optional[str] = Field(None, description="Protocol website URL")
    logo_url: Optional[str] = Field(None, description="Protocol logo URL")
    has_supported_portfolio: bool = Field(..., description="Whether portfolio tracking is supported")
    tvl: Optional[float] = Field(None, description="Total Value Locked (USD)")
    portfolio_item_list: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="List of portfolio items in this protocol"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "uniswap3",
                "chain": "eth",
                "name": "Uniswap V3",
                "site_url": "https://app.uniswap.org",
                "logo_url": "https://static.debank.com/image/project/logo_url/uniswap3/87a541b3b83b041c8d12119e5a0d19f0.png",
                "has_supported_portfolio": True,
                "tvl": 3500000000.0
            }
        }


class NFTModel(BaseModel):
    """NFT (Non-Fungible Token) information"""

    id: str = Field(..., description="NFT unique identifier")
    contract_id: str = Field(..., description="NFT contract address")
    chain: str = Field(..., description="Chain where NFT exists")
    name: str = Field(..., description="NFT name")
    description: Optional[str] = Field(None, description="NFT description")
    content_type: str = Field(..., description="Content type (image, video, etc.)")
    content: Optional[str] = Field(None, description="URL to NFT content")
    thumbnail_url: Optional[str] = Field(None, description="URL to thumbnail image")
    collection_id: Optional[str] = Field(None, description="Collection identifier")
    amount: Optional[int] = Field(None, description="Amount owned (for ERC-1155)")
    usd_price: Optional[float] = Field(None, description="Current USD price")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d_1234",
                "contract_id": "0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d",
                "chain": "eth",
                "name": "Bored Ape #1234",
                "description": "A unique Bored Ape NFT",
                "content_type": "image_url",
                "content": "https://example.com/ape.png",
                "thumbnail_url": "https://example.com/ape_thumb.png",
                "collection_id": "boredapeyachtclub",
                "amount": 1,
                "usd_price": 50000.0
            }
        }


class PortfolioItemModel(BaseModel):
    """Portfolio item (staking, lending, LP position, etc.)"""

    pool: Dict[str, Any] = Field(..., description="Pool information")
    asset_token_list: List[TokenModel] = Field(..., description="List of asset tokens")
    reward_token_list: Optional[List[TokenModel]] = Field(None, description="List of reward tokens")
    name: str = Field(..., description="Portfolio item name")
    detail_types: List[str] = Field(..., description="Detail types (e.g., 'common', 'locked')")
    stats: Dict[str, Any] = Field(..., description="Statistics (APY, TVL, etc.)")

    class Config:
        json_schema_extra = {
            "example": {
                "pool": {
                    "id": "0x1234...",
                    "chain": "eth",
                    "project_id": "aave3"
                },
                "asset_token_list": [],
                "reward_token_list": [],
                "name": "USDC Lending",
                "detail_types": ["common"],
                "stats": {
                    "asset_usd_value": 10000.0,
                    "debt_usd_value": 0.0,
                    "net_usd_value": 10000.0
                }
            }
        }


class TotalBalanceModel(BaseModel):
    """User's total balance across all chains"""

    total_usd_value: float = Field(..., description="Total portfolio value in USD")
    chain_list: List[Dict[str, Any]] = Field(..., description="Balance breakdown by chain")

    class Config:
        json_schema_extra = {
            "example": {
                "total_usd_value": 125000.0,
                "chain_list": [
                    {
                        "id": "eth",
                        "name": "Ethereum",
                        "usd_value": 100000.0
                    },
                    {
                        "id": "bsc",
                        "name": "BNB Chain",
                        "usd_value": 25000.0
                    }
                ]
            }
        }


class TransactionModel(BaseModel):
    """Transaction information"""

    id: str = Field(..., description="Transaction hash")
    chain: str = Field(..., description="Chain where transaction occurred")
    time_at: int = Field(..., description="Transaction timestamp (Unix time)")
    tx_type: Optional[str] = Field(None, description="Transaction type")
    tx: Dict[str, Any] = Field(..., description="Transaction details")
    sends: Optional[List[TokenModel]] = Field(None, description="Tokens sent")
    receives: Optional[List[TokenModel]] = Field(None, description="Tokens received")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "0xabc123...",
                "chain": "eth",
                "time_at": 1703001600,
                "tx_type": "swap",
                "tx": {
                    "from_addr": "0x1234...",
                    "to_addr": "0x5678...",
                    "value": 1000000000000000000,
                    "gas_used": 150000
                },
                "sends": [],
                "receives": []
            }
        }


class GasModel(BaseModel):
    """Gas price information"""

    chain_id: str = Field(..., description="Chain identifier")
    normal_price: float = Field(..., description="Normal gas price (Gwei)")
    fast_price: float = Field(..., description="Fast gas price (Gwei)")
    rapid_price: float = Field(..., description="Rapid gas price (Gwei)")
    base_fee: Optional[float] = Field(None, description="Base fee (Gwei, EIP-1559)")

    class Config:
        json_schema_extra = {
            "example": {
                "chain_id": "eth",
                "normal_price": 30.0,
                "fast_price": 35.0,
                "rapid_price": 40.0,
                "base_fee": 28.0
            }
        }


class WalletModel(BaseModel):
    """Wallet information"""

    id: str = Field(..., description="Wallet address")
    name: Optional[str] = Field(None, description="Wallet name/label")
    chains: List[str] = Field(..., description="Chains this wallet is active on")
    usd_value: float = Field(..., description="Total wallet value in USD")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "0x1234567890123456789012345678901234567890",
                "name": "Main Wallet",
                "chains": ["eth", "bsc", "matic"],
                "usd_value": 125000.0
            }
        }
