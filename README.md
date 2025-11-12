# MCP Server for DeBank API

A Model Context Protocol (MCP) server that provides seamless integration with the [DeBank API](https://docs.cloud.debank.com/), enabling AI assistants to access DeFi portfolio data, token information, and blockchain analytics.

## Features

- **Portfolio Management**: Access user balances, token holdings, and NFT collections
- **Token Information**: Query token prices, metadata, and market data
- **Protocol Analytics**: Get DeFi protocol information and user positions
- **Transaction History**: Retrieve and analyze transaction data
- **Multi-Chain Support**: Works across 40+ blockchain networks
- **Comprehensive Error Handling**: Robust error handling with user-friendly messages
- **Rate Limiting**: Automatic rate limit handling and retry logic

## Installation

### Using uvx (Recommended)

```bash
# Install and run directly
uvx mcp-server-debank

# Or install from source
git clone <repository-url>
cd mcp-server-debank
uvx --from . mcp-server-debank
```

### Using pip

```bash
pip install mcp-server-debank

# Or install from source
git clone <repository-url>
cd mcp-server-debank
pip install -e .
```

## Configuration

### 1. Get DeBank API Access Key

1. Visit [DeBank Cloud](https://cloud.debank.com/)
2. Sign up for an account
3. Generate an API access key from your dashboard

### 2. Set Environment Variable

Create a `.env` file in your project directory:

```bash
DEBANK_ACCESS_KEY=your_access_key_here
```

Or export it in your shell:

```bash
export DEBANK_ACCESS_KEY='your_access_key_here'
```

### 3. Configure Claude Desktop

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "debank": {
      "command": "uvx",
      "args": ["mcp-server-debank"],
      "env": {
        "DEBANK_ACCESS_KEY": "your_access_key_here"
      }
    }
  }
}
```

## Usage

Once configured, you can ask Claude to interact with DeBank data:

```
"What's the total balance for address 0x1234...?"
"Show me the token holdings for this wallet"
"What DeFi protocols is this address using?"
"Get the transaction history for the last 30 days"
```

## Available Tools

### User & Portfolio
- `get_user_balance` - Get total balance across all chains
- `get_user_token_list` - Get list of tokens held by user
- `get_user_nft_list` - Get NFT collection
- `get_user_protocol_list` - Get DeFi protocol positions

### Token Information
- `get_token_info` - Get detailed token information
- `get_token_price` - Get current token price
- `search_tokens` - Search for tokens by name or symbol

### Protocol & Chain
- `get_supported_chains` - List all supported blockchains
- `get_protocol_info` - Get protocol details
- `get_gas_price` - Get current gas prices

### Transactions
- `get_user_transactions` - Get transaction history
- `get_transaction_details` - Get detailed transaction information

## Development

### Project Structure

```
mcp-server-debank/
├── src/
│   └── mcp_server_debank/
│       ├── __init__.py          # Package initialization
│       ├── server.py            # FastMCP server and tool definitions
│       ├── client.py            # DeBank API HTTP client
│       ├── validators.py        # Input validation utilities
│       └── models.py            # Pydantic models for responses
├── tests/
│   ├── test_client.py           # Client tests
│   ├── test_tools.py            # Tool tests
│   └── test_validators.py      # Validator tests
├── examples/
│   └── usage_examples.py        # Usage examples
├── pyproject.toml               # Project metadata and dependencies
└── README.md                    # This file
```

### Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage
pytest --cov=mcp_server_debank

# Run specific test file
pytest tests/test_client.py

# Run specific test
pytest tests/test_client.py::test_validate_address
```

### Local Development

```bash
# Clone repository
git clone <repository-url>
cd mcp-server-debank

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Test the server with MCP inspector
mcp dev src/mcp_server_debank/server.py
```

## API Coverage

This server implements the following DeBank API endpoints:

- ✅ User information and balances
- ✅ Token information and prices
- ✅ Protocol and chain data
- ✅ Transaction history
- ✅ NFT collections
- ✅ Gas prices
- 🚧 Advanced analytics (coming soon)
- 🚧 Historical data (coming soon)

## Error Handling

The server provides comprehensive error handling:

- **Authentication Errors (401)**: Invalid access key
- **Authorization Errors (403)**: Capacity limits or insufficient permissions
- **Validation Errors (400)**: Invalid input parameters
- **Rate Limiting (429)**: Automatic retry with backoff
- **Server Errors (500)**: Graceful error messages
- **Network Errors**: Automatic retry with exponential backoff

## Rate Limits

DeBank API has rate limits based on your subscription tier. This server:
- Automatically detects rate limit responses
- Waits for the specified retry-after period
- Provides clear error messages when limits are exceeded

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

- **DeBank API Documentation**: https://docs.cloud.debank.com/
- **MCP Documentation**: https://modelcontextprotocol.io/
- **Issues**: Please report bugs via GitHub Issues

## Acknowledgments

Built with:
- [FastMCP](https://github.com/jlowin/fastmcp) - MCP server framework
- [httpx](https://www.python-httpx.org/) - HTTP client
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation
- [DeBank API](https://docs.cloud.debank.com/) - DeFi data provider
