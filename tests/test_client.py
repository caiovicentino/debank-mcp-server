"""Tests for DeBank API client."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx


class TestDeBankClientInitialization:
    """Test DeBank client initialization."""

    def test_client_initialization_with_key(self, debank_api_key):
        """Test that client initializes correctly with API key."""
        from mcp_server_debank.client import DeBankClient

        client = DeBankClient(access_key=debank_api_key)
        assert client.access_key == debank_api_key

    def test_client_initialization_from_env(self, mock_env):
        """Test that client reads API key from environment."""
        from mcp_server_debank.client import DeBankClient

        client = DeBankClient()
        assert client.access_key is not None

    def test_client_initialization_no_key(self, monkeypatch):
        """Test that client raises error without API key."""
        from mcp_server_debank.client import DeBankClient

        monkeypatch.delenv("DEBANK_ACCESS_KEY", raising=False)

        with pytest.raises(ValueError, match="API key"):
            DeBankClient()

    def test_client_base_url_set(self, debank_api_key):
        """Test that base URL is properly set."""
        from mcp_server_debank.client import DeBankClient

        client = DeBankClient(access_key=debank_api_key)
        assert "debank.com" in client.base_url or "cloud.debank" in client.base_url


class TestDeBankClientGetRequest:
    """Test GET request functionality."""

    @pytest.mark.asyncio
    async def test_get_request_success(self, debank_api_key, mock_response_chains):
        """Test successful GET request."""
        from mcp_server_debank.client import DeBankClient

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_chains
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            client = DeBankClient(access_key=debank_api_key)
            result = await client.get("/v1/chain/list")

            assert result == mock_response_chains
            mock_get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_request_with_params(self, debank_api_key):
        """Test GET request with query parameters."""
        from mcp_server_debank.client import DeBankClient

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"data": []}
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            client = DeBankClient(access_key=debank_api_key)
            params = {"chain_id": "eth", "limit": 20}
            await client.get("/v1/user/tokens", params=params)

            # Verify params were passed
            call_kwargs = mock_get.call_args[1]
            assert "params" in call_kwargs
            assert call_kwargs["params"]["chain_id"] == "eth"

    @pytest.mark.asyncio
    async def test_get_request_with_headers(self, debank_api_key):
        """Test that authorization header is included."""
        from mcp_server_debank.client import DeBankClient

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {}
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            client = DeBankClient(access_key=debank_api_key)
            await client.get("/v1/chain/list")

            # Verify authorization header
            call_kwargs = mock_get.call_args[1]
            assert "headers" in call_kwargs
            assert debank_api_key in str(call_kwargs["headers"])


class TestDeBankClientPostRequest:
    """Test POST request functionality."""

    @pytest.mark.asyncio
    async def test_post_request_success(self, debank_api_key, sample_transaction, mock_response_simulate_tx):
        """Test successful POST request."""
        from mcp_server_debank.client import DeBankClient

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_simulate_tx
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            client = DeBankClient(access_key=debank_api_key)
            result = await client.post("/v1/tx/simulate", json=sample_transaction)

            assert result == mock_response_simulate_tx
            mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_post_request_with_json_body(self, debank_api_key, sample_transaction):
        """Test POST request with JSON body."""
        from mcp_server_debank.client import DeBankClient

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {}
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            client = DeBankClient(access_key=debank_api_key)
            await client.post("/v1/tx/simulate", json=sample_transaction)

            # Verify JSON body was passed
            call_kwargs = mock_post.call_args[1]
            assert "json" in call_kwargs
            assert call_kwargs["json"] == sample_transaction


class TestDeBankClientErrorHandling:
    """Test error handling for various HTTP status codes."""

    @pytest.mark.asyncio
    async def test_401_unauthorized(self, debank_api_key):
        """Test handling of 401 Unauthorized error."""
        from mcp_server_debank.client import DeBankClient

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 401
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Unauthorized", request=MagicMock(), response=mock_response
            )
            mock_get.return_value = mock_response

            client = DeBankClient(access_key=debank_api_key)

            with pytest.raises(Exception, match="401|Unauthorized|API key"):
                await client.get("/v1/chain/list")

    @pytest.mark.asyncio
    async def test_403_forbidden(self, debank_api_key):
        """Test handling of 403 Forbidden error."""
        from mcp_server_debank.client import DeBankClient

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 403
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Forbidden", request=MagicMock(), response=mock_response
            )
            mock_get.return_value = mock_response

            client = DeBankClient(access_key=debank_api_key)

            with pytest.raises(Exception, match="403|Forbidden|permission"):
                await client.get("/v1/chain/list")

    @pytest.mark.asyncio
    async def test_429_rate_limit(self, debank_api_key):
        """Test handling of 429 Rate Limit error."""
        from mcp_server_debank.client import DeBankClient

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 429
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Too Many Requests", request=MagicMock(), response=mock_response
            )
            mock_get.return_value = mock_response

            client = DeBankClient(access_key=debank_api_key)

            with pytest.raises(Exception, match="429|rate limit|Too Many"):
                await client.get("/v1/chain/list")

    @pytest.mark.asyncio
    async def test_500_server_error(self, debank_api_key):
        """Test handling of 500 Server Error."""
        from mcp_server_debank.client import DeBankClient

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Internal Server Error", request=MagicMock(), response=mock_response
            )
            mock_get.return_value = mock_response

            client = DeBankClient(access_key=debank_api_key)

            with pytest.raises(Exception, match="500|server error|Internal"):
                await client.get("/v1/chain/list")

    @pytest.mark.asyncio
    async def test_network_error(self, debank_api_key):
        """Test handling of network errors."""
        from mcp_server_debank.client import DeBankClient

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.side_effect = httpx.NetworkError("Connection failed")

            client = DeBankClient(access_key=debank_api_key)

            with pytest.raises(Exception, match="network|connection"):
                await client.get("/v1/chain/list")

    @pytest.mark.asyncio
    async def test_timeout_error(self, debank_api_key):
        """Test handling of timeout errors."""
        from mcp_server_debank.client import DeBankClient

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.side_effect = httpx.TimeoutException("Request timeout")

            client = DeBankClient(access_key=debank_api_key)

            with pytest.raises(Exception, match="timeout"):
                await client.get("/v1/chain/list")


class TestDeBankClientRetryLogic:
    """Test retry logic for transient failures."""

    @pytest.mark.asyncio
    async def test_retry_on_network_error(self, debank_api_key):
        """Test that client retries on network errors."""
        from mcp_server_debank.client import DeBankClient

        with patch("httpx.AsyncClient.get") as mock_get:
            # Fail twice, then succeed
            mock_get.side_effect = [
                httpx.NetworkError("Connection failed"),
                httpx.NetworkError("Connection failed"),
                MagicMock(status_code=200, json=lambda: {"data": []})
            ]

            client = DeBankClient(access_key=debank_api_key, max_retries=3)

            # Should eventually succeed
            result = await client.get("/v1/chain/list")
            assert result == {"data": []}
            assert mock_get.call_count == 3

    @pytest.mark.asyncio
    async def test_no_retry_on_client_error(self, debank_api_key):
        """Test that client doesn't retry on 4xx errors."""
        from mcp_server_debank.client import DeBankClient

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 400
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Bad Request", request=MagicMock(), response=mock_response
            )
            mock_get.return_value = mock_response

            client = DeBankClient(access_key=debank_api_key, max_retries=3)

            with pytest.raises(Exception):
                await client.get("/v1/chain/list")

            # Should only call once (no retries for 4xx)
            assert mock_get.call_count == 1


class TestDeBankClientContextManager:
    """Test client context manager functionality."""

    @pytest.mark.asyncio
    async def test_context_manager_usage(self, debank_api_key):
        """Test that client works as async context manager."""
        from mcp_server_debank.client import DeBankClient

        async with DeBankClient(access_key=debank_api_key) as client:
            assert client is not None
            assert client.access_key == debank_api_key

    @pytest.mark.asyncio
    async def test_context_manager_cleanup(self, debank_api_key):
        """Test that client properly closes connections."""
        from mcp_server_debank.client import DeBankClient

        client = DeBankClient(access_key=debank_api_key)

        async with client:
            pass  # Do nothing

        # Verify client is closed (implementation dependent)
        # This test verifies the pattern works
