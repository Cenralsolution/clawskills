"""
Shared utilities for OpenClaw skills
Provides common functions for security, validation, and error handling
"""

import os
import re
import logging
from typing import Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class SecurityError(Exception):
    """Raised when security validation fails"""
    pass


class ValidationError(Exception):
    """Raised when input validation fails"""
    pass


def get_secure_api_key(key_name: str) -> str:
    """
    Retrieve API key from environment variables securely.
    
    Args:
        key_name: Name of the environment variable
        
    Returns:
        API key value
        
    Raises:
        SecurityError: If API key is not found
    """
    api_key = os.getenv(key_name)
    if not api_key:
        raise SecurityError(f"API key '{key_name}' not found in environment variables")
    return api_key


def validate_string_input(value: Any, field_name: str, 
                         min_length: int = 1, 
                         max_length: int = 1000,
                         allowed_chars: Optional[str] = None) -> str:
    """
    Validate and sanitize string input.
    
    Args:
        value: Input value to validate
        field_name: Name of the field for error messages
        min_length: Minimum allowed length
        max_length: Maximum allowed length
        allowed_chars: Regex pattern for allowed characters (None = all allowed)
        
    Returns:
        Validated and stripped string
        
    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(value, str):
        raise ValidationError(f"{field_name} must be a string, got {type(value).__name__}")
    
    value = value.strip()
    
    if len(value) < min_length:
        raise ValidationError(f"{field_name} must be at least {min_length} characters long")
    
    if len(value) > max_length:
        raise ValidationError(f"{field_name} must not exceed {max_length} characters")
    
    if allowed_chars and not re.match(f"^[{allowed_chars}]+$", value):
        raise ValidationError(f"{field_name} contains invalid characters")
    
    return value


def validate_theme(theme: str) -> str:
    """
    Validate theme/topic parameter.
    
    Args:
        theme: Theme or topic string
        
    Returns:
        Validated theme string
        
    Raises:
        ValidationError: If validation fails
    """
    return validate_string_input(
        theme,
        "theme",
        min_length=3,
        max_length=500,
        allowed_chars=r"a-zA-Z0-9\s\-_,."
    )


def safe_log_api_call(api_name: str, operation: str, 
                     status: str, details: dict = None) -> None:
    """
    Log API calls safely without exposing sensitive data.
    
    Args:
        api_name: Name of the API being called
        operation: Operation being performed
        status: Status of the operation (success/error/timeout)
        details: Additional details (sensitive values will be masked)
    """
    safe_details = details.copy() if details else {}
    # Mask any keys that contain sensitive info
    sensitive_keys = ['api_key', 'token', 'secret', 'password']
    for key in sensitive_keys:
        if key in safe_details:
            safe_details[key] = '***REDACTED***'
    
    log_msg = f"API: {api_name} | Operation: {operation} | Status: {status}"
    if safe_details:
        log_msg += f" | Details: {safe_details}"
    
    if status == 'error':
        logger.error(log_msg)
    else:
        logger.info(log_msg)


def get_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return datetime.utcnow().isoformat() + "Z"
