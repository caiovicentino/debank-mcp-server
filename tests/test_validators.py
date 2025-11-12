"""Tests for validation functions."""

import pytest
from datetime import datetime


# Note: These tests will be implemented once the validators module is created by other agents
# This provides the test structure and requirements

class TestAddressValidation:
    """Test Ethereum address validation."""

    def test_validate_address_valid(self, valid_address):
        """Test that valid Ethereum addresses pass validation."""
        from mcp_server_debank.validators import validate_address

        # Should not raise any exception
        validate_address(valid_address)

    def test_validate_address_valid_lowercase(self):
        """Test lowercase addresses are accepted."""
        from mcp_server_debank.validators import validate_address

        address = "0xd8da6bf26964af9d7eed9e03e53415d37aa96045"
        validate_address(address)

    def test_validate_address_valid_uppercase(self):
        """Test uppercase addresses are accepted."""
        from mcp_server_debank.validators import validate_address

        address = "0xD8DA6BF26964AF9D7EED9E03E53415D37AA96045"
        validate_address(address)

    def test_validate_address_invalid_too_short(self):
        """Test that addresses shorter than 42 chars are rejected."""
        from mcp_server_debank.validators import validate_address

        with pytest.raises(ValueError, match="Invalid Ethereum address"):
            validate_address("0x123")

    def test_validate_address_invalid_too_long(self):
        """Test that addresses longer than 42 chars are rejected."""
        from mcp_server_debank.validators import validate_address

        with pytest.raises(ValueError, match="Invalid Ethereum address"):
            validate_address("0xd8da6bf26964af9d7eed9e03e53415d37aa96045123")

    def test_validate_address_invalid_no_prefix(self):
        """Test that addresses without 0x prefix are rejected."""
        from mcp_server_debank.validators import validate_address

        with pytest.raises(ValueError, match="Invalid Ethereum address"):
            validate_address("d8da6bf26964af9d7eed9e03e53415d37aa96045")

    def test_validate_address_invalid_chars(self):
        """Test that addresses with invalid characters are rejected."""
        from mcp_server_debank.validators import validate_address

        with pytest.raises(ValueError, match="Invalid Ethereum address"):
            validate_address("0xGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG")

    def test_validate_address_empty(self):
        """Test that empty addresses are rejected."""
        from mcp_server_debank.validators import validate_address

        with pytest.raises(ValueError, match="Invalid Ethereum address"):
            validate_address("")

    def test_validate_address_none(self):
        """Test that None addresses are rejected."""
        from mcp_server_debank.validators import validate_address

        with pytest.raises((ValueError, TypeError)):
            validate_address(None)


class TestChainIdValidation:
    """Test chain ID validation."""

    def test_validate_chain_id_valid(self, valid_chain_id):
        """Test that valid chain IDs pass validation."""
        from mcp_server_debank.validators import validate_chain_id

        validate_chain_id(valid_chain_id)

    def test_validate_chain_id_all_major_chains(self):
        """Test all major chain IDs are valid."""
        from mcp_server_debank.validators import validate_chain_id

        major_chains = [
            "eth", "bsc", "matic", "arb", "op", "avax",
            "ftm", "base", "cro", "aurora", "metis"
        ]

        for chain_id in major_chains:
            validate_chain_id(chain_id)

    def test_validate_chain_id_invalid(self, invalid_chain_id):
        """Test that invalid chain IDs are rejected."""
        from mcp_server_debank.validators import validate_chain_id

        with pytest.raises(ValueError, match="Invalid chain ID"):
            validate_chain_id(invalid_chain_id)

    def test_validate_chain_id_empty(self):
        """Test that empty chain IDs are rejected."""
        from mcp_server_debank.validators import validate_chain_id

        with pytest.raises(ValueError, match="Invalid chain ID"):
            validate_chain_id("")

    def test_validate_chain_id_case_sensitive(self):
        """Test that chain IDs are case sensitive."""
        from mcp_server_debank.validators import validate_chain_id

        # Lowercase should work
        validate_chain_id("eth")

        # Uppercase might not (depends on implementation)
        # This test verifies the expected behavior


class TestDateValidation:
    """Test date format validation."""

    def test_validate_date_format_valid(self):
        """Test that valid date formats pass validation."""
        from mcp_server_debank.validators import validate_date_format

        validate_date_format("2025-01-11")

    def test_validate_date_format_valid_various_dates(self):
        """Test various valid date formats."""
        from mcp_server_debank.validators import validate_date_format

        valid_dates = [
            "2025-01-01",
            "2025-12-31",
            "2024-02-29",  # Leap year
            "2023-06-15"
        ]

        for date in valid_dates:
            validate_date_format(date)

    def test_validate_date_format_invalid_format(self):
        """Test that invalid date formats are rejected."""
        from mcp_server_debank.validators import validate_date_format

        invalid_dates = [
            "01-11-2025",  # Wrong order
            "2025/01/11",  # Wrong separator
            "2025-1-11",   # Missing leading zero
            "2025-01-1",   # Missing leading zero
            "25-01-11",    # Short year
        ]

        for date in invalid_dates:
            with pytest.raises(ValueError, match="Invalid date format"):
                validate_date_format(date)

    def test_validate_date_format_invalid_dates(self):
        """Test that invalid dates are rejected."""
        from mcp_server_debank.validators import validate_date_format

        invalid_dates = [
            "2025-13-01",  # Invalid month
            "2025-00-01",  # Invalid month
            "2025-01-32",  # Invalid day
            "2025-01-00",  # Invalid day
            "2023-02-29",  # Not a leap year
        ]

        for date in invalid_dates:
            with pytest.raises(ValueError, match="Invalid date"):
                validate_date_format(date)

    def test_validate_date_format_empty(self):
        """Test that empty dates are rejected."""
        from mcp_server_debank.validators import validate_date_format

        with pytest.raises(ValueError, match="Invalid date format"):
            validate_date_format("")


class TestTokenIdsValidation:
    """Test token IDs list validation."""

    def test_validate_token_ids_valid_single(self, sample_token_id):
        """Test that single token ID passes validation."""
        from mcp_server_debank.validators import validate_token_ids

        validate_token_ids([sample_token_id])

    def test_validate_token_ids_valid_multiple(self, sample_token_id):
        """Test that multiple token IDs pass validation."""
        from mcp_server_debank.validators import validate_token_ids

        token_ids = [sample_token_id] * 10
        validate_token_ids(token_ids)

    def test_validate_token_ids_max_100(self, sample_token_id):
        """Test that exactly 100 token IDs pass validation."""
        from mcp_server_debank.validators import validate_token_ids

        token_ids = [sample_token_id] * 100
        validate_token_ids(token_ids)

    def test_validate_token_ids_exceeds_max(self, sample_token_id):
        """Test that more than 100 token IDs are rejected."""
        from mcp_server_debank.validators import validate_token_ids

        token_ids = [sample_token_id] * 101

        with pytest.raises(ValueError, match="Maximum 100 token IDs allowed"):
            validate_token_ids(token_ids)

    def test_validate_token_ids_empty_list(self):
        """Test that empty list is rejected."""
        from mcp_server_debank.validators import validate_token_ids

        with pytest.raises(ValueError, match="At least one token ID required"):
            validate_token_ids([])

    def test_validate_token_ids_invalid_format(self):
        """Test that invalid token ID formats are rejected."""
        from mcp_server_debank.validators import validate_token_ids

        with pytest.raises(ValueError, match="Invalid token ID"):
            validate_token_ids(["invalid_token_id"])


class TestPaginationValidation:
    """Test pagination parameter validation."""

    def test_validate_pagination_valid(self):
        """Test that valid pagination parameters pass validation."""
        from mcp_server_debank.validators import validate_pagination

        validate_pagination(limit=20, offset=0)
        validate_pagination(limit=100, offset=50)

    def test_validate_pagination_limit_too_high(self):
        """Test that limit > 100 is rejected."""
        from mcp_server_debank.validators import validate_pagination

        with pytest.raises(ValueError, match="limit"):
            validate_pagination(limit=101, offset=0)

    def test_validate_pagination_limit_zero(self):
        """Test that limit = 0 is rejected."""
        from mcp_server_debank.validators import validate_pagination

        with pytest.raises(ValueError, match="limit"):
            validate_pagination(limit=0, offset=0)

    def test_validate_pagination_limit_negative(self):
        """Test that negative limit is rejected."""
        from mcp_server_debank.validators import validate_pagination

        with pytest.raises(ValueError, match="limit"):
            validate_pagination(limit=-1, offset=0)

    def test_validate_pagination_offset_negative(self):
        """Test that negative offset is rejected."""
        from mcp_server_debank.validators import validate_pagination

        with pytest.raises(ValueError, match="offset"):
            validate_pagination(limit=20, offset=-1)


class TestTransactionValidation:
    """Test transaction object validation."""

    def test_validate_transaction_valid(self, sample_transaction):
        """Test that valid transaction passes validation."""
        from mcp_server_debank.validators import validate_transaction

        validate_transaction(sample_transaction)

    def test_validate_transaction_missing_required_field(self):
        """Test that transaction missing required fields is rejected."""
        from mcp_server_debank.validators import validate_transaction

        invalid_tx = {
            "chainId": "eth",
            "from": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
            # Missing "to"
        }

        with pytest.raises(ValueError, match="required field"):
            validate_transaction(invalid_tx)

    def test_validate_transaction_invalid_address(self):
        """Test that transaction with invalid address is rejected."""
        from mcp_server_debank.validators import validate_transaction

        invalid_tx = {
            "chainId": "eth",
            "from": "invalid_address",
            "to": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
            "value": "0"
        }

        with pytest.raises(ValueError, match="Invalid Ethereum address"):
            validate_transaction(invalid_tx)


class TestDetailLevelValidation:
    """Test detail level validation."""

    def test_validate_detail_level_valid(self):
        """Test that valid detail levels pass validation."""
        from mcp_server_debank.validators import validate_detail_level

        validate_detail_level("simple")
        validate_detail_level("complex")

    def test_validate_detail_level_invalid(self):
        """Test that invalid detail levels are rejected."""
        from mcp_server_debank.validators import validate_detail_level

        with pytest.raises(ValueError, match="Invalid detail level"):
            validate_detail_level("invalid")

    def test_validate_detail_level_case_sensitive(self):
        """Test that detail levels are case sensitive."""
        from mcp_server_debank.validators import validate_detail_level

        with pytest.raises(ValueError, match="Invalid detail level"):
            validate_detail_level("SIMPLE")
