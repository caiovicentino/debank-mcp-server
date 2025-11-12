"""
DeBank API HTTP Client

Provides an async HTTP client for interacting with the DeBank API
with proper authentication, error handling, and rate limiting.
"""

import asyncio
from typing import Any, Optional
import httpx
from datetime import datetime, timedelta


class DeBankAPIError(Exception):
    """Base exception for DeBank API errors"""
    pass


class DeBankAuthError(DeBankAPIError):
    """Authentication or authorization errors"""
    pass


class DeBankRateLimitError(DeBankAPIError):
    """Rate limiting errors"""

    def __init__(self, message: str, retry_after: Optional[int] = None):
        super().__init__(message)
        self.retry_after = retry_after


class DeBankValidationError(DeBankAPIError):
    """Request validation errors"""
    pass


class DeBankClient:
    """
    Async HTTP client for DeBank API with authentication and error handling.

    Features:
    - Automatic authentication via AccessKey header
    - Comprehensive error handling for all API error codes
    - Rate limiting support with retry-after handling
    - Request/response logging
    - Connection pooling and timeout management

    Args:
        access_key: DeBank API access key for authentication
        base_url: Base URL for DeBank API (defaults to production)
        timeout: Request timeout in seconds
        max_retries: Maximum number of retries for transient errors
    """

    def __init__(
        self,
        access_key: str,
        base_url: str = "https://pro-openapi.debank.com",
        timeout: float = 30.0,
        max_retries: int = 3
    ):
        if not access_key:
            raise ValueError("access_key is required")

        self.base_url = base_url.rstrip("/")
        self.access_key = access_key
        self.max_retries = max_retries

        # Initialize async HTTP client with connection pooling
        # Note: Don't set Content-Type in default headers - GET requests don't need it
        # and DeBank API rejects GET with Content-Type: application/json
        self.client = httpx.AsyncClient(
            headers={
                "AccessKey": access_key,
                "Accept": "application/json",
            },
            timeout=httpx.Timeout(timeout),
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
        )

        # Rate limiting tracking
        self._rate_limit_reset: Optional[datetime] = None
        self._requests_remaining: Optional[int] = None

    async def get(
        self,
        endpoint: str,
        params: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """
        Make GET request to DeBank API with error handling.

        Args:
            endpoint: API endpoint path (without base URL)
            params: Query parameters as dictionary

        Returns:
            Response data as dictionary

        Raises:
            DeBankAuthError: Authentication/authorization failed
            DeBankRateLimitError: Rate limit exceeded
            DeBankValidationError: Invalid request parameters
            DeBankAPIError: Other API errors
        """
        endpoint = endpoint.lstrip("/")
        url = f"{self.base_url}/{endpoint}"

        # Check rate limit before making request
        await self._check_rate_limit()

        # Clean None values from params
        if params:
            params = {k: v for k, v in params.items() if v is not None}

        retries = 0
        last_error = None

        while retries <= self.max_retries:
            try:
                response = await self.client.get(url, params=params)

                # Update rate limit info from headers
                self._update_rate_limit_info(response)

                # Handle different status codes
                if response.status_code == 200:
                    return response.json()

                # Handle errors
                await self._handle_error_response(response)

            except httpx.TimeoutException as e:
                last_error = DeBankAPIError(f"Request timeout: {str(e)}")
                retries += 1
                if retries <= self.max_retries:
                    await asyncio.sleep(2 ** retries)  # Exponential backoff
                continue

            except httpx.NetworkError as e:
                last_error = DeBankAPIError(f"Network error: {str(e)}")
                retries += 1
                if retries <= self.max_retries:
                    await asyncio.sleep(2 ** retries)
                continue

            except DeBankRateLimitError as e:
                # Don't retry rate limit errors, propagate immediately
                raise

            break

        # If we exhausted retries, raise the last error
        if last_error:
            raise last_error

        raise DeBankAPIError("Request failed after maximum retries")

    async def post(
        self,
        endpoint: str,
        data: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """
        Make POST request to DeBank API (for transaction endpoints).

        Args:
            endpoint: API endpoint path (without base URL)
            data: Request body as dictionary

        Returns:
            Response data as dictionary

        Raises:
            DeBankAuthError: Authentication/authorization failed
            DeBankRateLimitError: Rate limit exceeded
            DeBankValidationError: Invalid request parameters
            DeBankAPIError: Other API errors
        """
        endpoint = endpoint.lstrip("/")
        url = f"{self.base_url}/{endpoint}"

        # Check rate limit before making request
        await self._check_rate_limit()

        retries = 0
        last_error = None

        while retries <= self.max_retries:
            try:
                response = await self.client.post(url, json=data or {})

                # Update rate limit info from headers
                self._update_rate_limit_info(response)

                # Handle different status codes
                if response.status_code == 200:
                    return response.json()

                # Handle errors
                await self._handle_error_response(response)

            except httpx.TimeoutException as e:
                last_error = DeBankAPIError(f"Request timeout: {str(e)}")
                retries += 1
                if retries <= self.max_retries:
                    await asyncio.sleep(2 ** retries)
                continue

            except httpx.NetworkError as e:
                last_error = DeBankAPIError(f"Network error: {str(e)}")
                retries += 1
                if retries <= self.max_retries:
                    await asyncio.sleep(2 ** retries)
                continue

            except DeBankRateLimitError as e:
                raise

            break

        if last_error:
            raise last_error

        raise DeBankAPIError("Request failed after maximum retries")

    async def _handle_error_response(self, response: httpx.Response) -> None:
        """
        Handle error responses from DeBank API.

        Args:
            response: HTTP response object

        Raises:
            Appropriate DeBankError subclass based on status code
        """
        status = response.status_code

        # Try to get error message from response
        try:
            error_data = response.json()
            error_message = error_data.get("error", {}).get("message", response.text)
        except Exception:
            error_message = response.text or f"HTTP {status}"

        # 400 Bad Request - validation error
        if status == 400:
            raise DeBankValidationError(
                f"Invalid request parameters: {error_message}"
            )

        # 401 Unauthorized - invalid access key
        elif status == 401:
            raise DeBankAuthError(
                "Authentication failed. Please check your DeBank API access key."
            )

        # 403 Forbidden - capacity limit or insufficient permissions
        elif status == 403:
            raise DeBankAuthError(
                f"Access forbidden: {error_message}. "
                "This may be due to capacity limits or insufficient permissions."
            )

        # 429 Too Many Requests - rate limit exceeded
        elif status == 429:
            retry_after = response.headers.get("Retry-After")
            retry_after_int = int(retry_after) if retry_after else 60

            raise DeBankRateLimitError(
                f"Rate limit exceeded. Please retry after {retry_after_int} seconds.",
                retry_after=retry_after_int
            )

        # 500 Internal Server Error
        elif status == 500:
            raise DeBankAPIError(
                f"DeBank API internal error: {error_message}. Please try again later."
            )

        # Other errors
        else:
            raise DeBankAPIError(
                f"API request failed with status {status}: {error_message}"
            )

    def _update_rate_limit_info(self, response: httpx.Response) -> None:
        """
        Update rate limit information from response headers.

        Args:
            response: HTTP response object
        """
        # Check for rate limit headers (adjust based on DeBank's actual headers)
        if "X-RateLimit-Remaining" in response.headers:
            try:
                self._requests_remaining = int(response.headers["X-RateLimit-Remaining"])
            except (ValueError, TypeError):
                pass

        if "X-RateLimit-Reset" in response.headers:
            try:
                reset_timestamp = int(response.headers["X-RateLimit-Reset"])
                self._rate_limit_reset = datetime.fromtimestamp(reset_timestamp)
            except (ValueError, TypeError):
                pass

    async def _check_rate_limit(self) -> None:
        """
        Check if we should wait before making the next request.
        Sleeps if rate limit reset time hasn't been reached.
        """
        if self._rate_limit_reset and self._requests_remaining is not None:
            if self._requests_remaining == 0:
                now = datetime.now()
                if now < self._rate_limit_reset:
                    wait_seconds = (self._rate_limit_reset - now).total_seconds()
                    if wait_seconds > 0:
                        await asyncio.sleep(wait_seconds)

    async def close(self) -> None:
        """
        Close the HTTP client and cleanup resources.
        Should be called when done using the client.
        """
        await self.client.aclose()

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()

    def __del__(self):
        """Ensure client is closed on deletion"""
        try:
            if hasattr(self, 'client') and not self.client.is_closed:
                # Try to close synchronously if event loop exists
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        loop.create_task(self.client.aclose())
                    else:
                        loop.run_until_complete(self.client.aclose())
                except RuntimeError:
                    pass
        except Exception:
            pass

    # ========================================================================
    # CONVENIENCE METHODS FOR ADVANCED TOOLS
    # ========================================================================

    async def get_gas_market(self, chain_id: str) -> list:
        """Get current gas prices for a blockchain."""
        return await self.get("/v1/wallet/gas_market", params={"chain_id": chain_id})

    async def get_user_total_net_curve(
        self,
        user_addr: str,
        chain_ids: Optional[str] = None
    ) -> list:
        """Get user's 24h total net curve (across all chains or specific chains)."""
        params = {"id": user_addr}
        if chain_ids:
            params["chain_ids"] = chain_ids
        return await self.get("/v1/user/total_net_curve", params=params)

    async def get_user_chain_net_curve(
        self,
        user_addr: str,
        chain_id: str
    ) -> list:
        """Get user's 24h net curve for a specific chain."""
        return await self.get(
            "/v1/user/chain_net_curve",
            params={"id": user_addr, "chain_id": chain_id}
        )

    async def get_pool(self, pool_id: str, chain_id: str) -> dict:
        """Get liquidity pool information."""
        return await self.get(
            "/v1/pool",
            params={"id": pool_id, "chain_id": chain_id}
        )

    async def get_account_units(self) -> dict:
        """Get API units balance and 30-day usage stats."""
        return await self.get("/v1/account/units")

    async def explain_tx(
        self,
        tx: dict,
        pending_txs: Optional[list] = None
    ) -> dict:
        """Explain a transaction before execution."""
        data = {"tx": tx}
        if pending_txs:
            data["pending_tx_list"] = pending_txs
        return await self.post("/v1/wallet/explain_tx", data=data)

    async def pre_exec_tx(
        self,
        tx: dict,
        pending_txs: Optional[list] = None
    ) -> dict:
        """Pre-execute a transaction to simulate its effects."""
        data = {"tx": tx}
        if pending_txs:
            data["pending_tx_list"] = pending_txs
        return await self.post("/v1/wallet/pre_exec_tx", data=data)
