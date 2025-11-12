"""
Input validation utilities for DeBank API requests.

Provides validation functions for common input types including
addresses, chain IDs, dates, and token identifiers.
"""

import re
from datetime import datetime
from typing import List, Optional


def validate_address(address: str) -> str:
    """
    Validate Ethereum address format.

    Checks that the address:
    - Starts with '0x'
    - Contains exactly 40 hexadecimal characters after '0x'
    - Is a valid hex string

    Args:
        address: Ethereum address string to validate

    Returns:
        Lowercase address string if valid

    Raises:
        ValueError: If address format is invalid

    Examples:
        >>> validate_address("0x1234567890123456789012345678901234567890")
        '0x1234567890123456789012345678901234567890'

        >>> validate_address("invalid")
        ValueError: Invalid Ethereum address format
    """
    if not address:
        raise ValueError("Address cannot be empty")

    if not isinstance(address, str):
        raise ValueError("Address must be a string")

    # Remove whitespace
    address = address.strip()

    # Check format: 0x followed by 40 hex characters
    if not re.match(r'^0x[0-9a-fA-F]{40}$', address):
        raise ValueError(
            "Invalid Ethereum address format. "
            "Address must start with '0x' followed by 40 hexadecimal characters. "
            f"Got: {address}"
        )

    # Return lowercase for consistency
    return address.lower()


def validate_chain_id(
    chain_id: str,
    supported_chains: Optional[List[str]] = None
) -> str:
    """
    Validate chain ID against supported chains.

    Args:
        chain_id: Chain identifier to validate
        supported_chains: Optional list of supported chain IDs.
                         If None, only basic validation is performed.

    Returns:
        Validated chain ID string

    Raises:
        ValueError: If chain_id is invalid or not supported

    Examples:
        >>> validate_chain_id("eth", ["eth", "bsc", "matic"])
        'eth'

        >>> validate_chain_id("unknown", ["eth", "bsc"])
        ValueError: Chain 'unknown' is not supported
    """
    if not chain_id:
        raise ValueError("Chain ID cannot be empty")

    if not isinstance(chain_id, str):
        raise ValueError("Chain ID must be a string")

    chain_id = chain_id.strip().lower()

    if not chain_id:
        raise ValueError("Chain ID cannot be empty or whitespace only")

    # Check against supported chains if provided
    if supported_chains is not None:
        supported_lower = [c.lower() for c in supported_chains]
        if chain_id not in supported_lower:
            raise ValueError(
                f"Chain '{chain_id}' is not supported. "
                f"Supported chains: {', '.join(supported_chains)}"
            )

    return chain_id


def validate_date_format(date_str: str, format_spec: str = "%Y-%m-%d") -> str:
    """
    Validate date string format.

    Args:
        date_str: Date string to validate
        format_spec: Expected date format (default: YYYY-MM-DD)

    Returns:
        Validated date string in the specified format

    Raises:
        ValueError: If date format is invalid

    Examples:
        >>> validate_date_format("2024-01-15")
        '2024-01-15'

        >>> validate_date_format("2024-13-45")
        ValueError: Invalid date format
    """
    if not date_str:
        raise ValueError("Date string cannot be empty")

    if not isinstance(date_str, str):
        raise ValueError("Date must be a string")

    date_str = date_str.strip()

    try:
        # Parse the date to validate format
        parsed_date = datetime.strptime(date_str, format_spec)

        # Return in the same format
        return parsed_date.strftime(format_spec)

    except ValueError as e:
        raise ValueError(
            f"Invalid date format. Expected format: {format_spec}. "
            f"Got: {date_str}. Error: {str(e)}"
        )


def validate_token_ids(token_ids: List[str], max_count: int = 100) -> List[str]:
    """
    Validate list of token IDs.

    Checks that:
    - Input is a list
    - List is not empty
    - List doesn't exceed maximum count
    - All token IDs are non-empty strings

    Args:
        token_ids: List of token identifier strings
        max_count: Maximum allowed number of token IDs (default: 100)

    Returns:
        Validated list of token ID strings

    Raises:
        ValueError: If validation fails

    Examples:
        >>> validate_token_ids(["eth", "usdc", "usdt"])
        ['eth', 'usdc', 'usdt']

        >>> validate_token_ids([])
        ValueError: Token IDs list cannot be empty
    """
    if not isinstance(token_ids, list):
        raise ValueError("Token IDs must be provided as a list")

    if len(token_ids) == 0:
        raise ValueError("Token IDs list cannot be empty")

    if len(token_ids) > max_count:
        raise ValueError(
            f"Too many token IDs provided. Maximum allowed: {max_count}, "
            f"got: {len(token_ids)}"
        )

    # Validate each token ID
    validated_ids = []
    for i, token_id in enumerate(token_ids):
        if not isinstance(token_id, str):
            raise ValueError(f"Token ID at index {i} must be a string, got: {type(token_id)}")

        token_id = token_id.strip()
        if not token_id:
            raise ValueError(f"Token ID at index {i} cannot be empty or whitespace only")

        validated_ids.append(token_id)

    return validated_ids


def validate_protocol_id(protocol_id: str) -> str:
    """
    Validate protocol ID format.

    Args:
        protocol_id: Protocol identifier to validate

    Returns:
        Validated protocol ID string

    Raises:
        ValueError: If protocol_id is invalid
    """
    if not protocol_id:
        raise ValueError("Protocol ID cannot be empty")

    if not isinstance(protocol_id, str):
        raise ValueError("Protocol ID must be a string")

    protocol_id = protocol_id.strip()

    if not protocol_id:
        raise ValueError("Protocol ID cannot be empty or whitespace only")

    return protocol_id


def validate_pagination_params(
    page_num: Optional[int] = None,
    page_count: Optional[int] = None,
    max_page_count: int = 100
) -> tuple[Optional[int], Optional[int]]:
    """
    Validate pagination parameters.

    Args:
        page_num: Page number (1-indexed)
        page_count: Number of items per page
        max_page_count: Maximum allowed items per page

    Returns:
        Tuple of (validated_page_num, validated_page_count)

    Raises:
        ValueError: If pagination parameters are invalid
    """
    if page_num is not None:
        if not isinstance(page_num, int):
            raise ValueError("page_num must be an integer")
        if page_num < 1:
            raise ValueError("page_num must be >= 1")

    if page_count is not None:
        if not isinstance(page_count, int):
            raise ValueError("page_count must be an integer")
        if page_count < 1:
            raise ValueError("page_count must be >= 1")
        if page_count > max_page_count:
            raise ValueError(
                f"page_count cannot exceed {max_page_count}, got: {page_count}"
            )

    return page_num, page_count


def validate_time_range(
    start_time: Optional[int] = None,
    end_time: Optional[int] = None
) -> tuple[Optional[int], Optional[int]]:
    """
    Validate Unix timestamp time range.

    Args:
        start_time: Start timestamp (Unix time in seconds)
        end_time: End timestamp (Unix time in seconds)

    Returns:
        Tuple of (validated_start_time, validated_end_time)

    Raises:
        ValueError: If time range is invalid
    """
    if start_time is not None:
        if not isinstance(start_time, int):
            raise ValueError("start_time must be an integer (Unix timestamp)")
        if start_time < 0:
            raise ValueError("start_time must be a positive Unix timestamp")

    if end_time is not None:
        if not isinstance(end_time, int):
            raise ValueError("end_time must be an integer (Unix timestamp)")
        if end_time < 0:
            raise ValueError("end_time must be a positive Unix timestamp")

    if start_time is not None and end_time is not None:
        if start_time >= end_time:
            raise ValueError("start_time must be less than end_time")

    return start_time, end_time


def validate_tx_hash(tx_hash: str) -> str:
    """
    Validate transaction hash format.

    Args:
        tx_hash: Transaction hash to validate

    Returns:
        Validated transaction hash (lowercase)

    Raises:
        ValueError: If transaction hash format is invalid
    """
    if not tx_hash:
        raise ValueError("Transaction hash cannot be empty")

    if not isinstance(tx_hash, str):
        raise ValueError("Transaction hash must be a string")

    tx_hash = tx_hash.strip()

    # Transaction hash should be 0x followed by 64 hex characters
    if not re.match(r'^0x[0-9a-fA-F]{64}$', tx_hash):
        raise ValueError(
            "Invalid transaction hash format. "
            "Hash must start with '0x' followed by 64 hexadecimal characters. "
            f"Got: {tx_hash}"
        )

    return tx_hash.lower()
