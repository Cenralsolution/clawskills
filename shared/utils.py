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


# ============================================================================
# GITHUB AUTHENTICATION & UTILITIES
# ============================================================================

def validate_repository_url(url: str) -> str:
    """
    Validate and normalize GitHub repository URL.
    
    Args:
        url: Repository URL (https://github.com/owner/repo or owner/repo)
        
    Returns:
        Normalized HTTPS URL
        
    Raises:
        ValidationError: If URL is invalid
    """
    if not isinstance(url, str):
        raise ValidationError("Repository URL must be a string")
    
    url = url.strip()
    
    # Accept owner/repo format
    if '/' in url and not url.startswith('http'):
        return f"https://github.com/{url}.git"
    
    # Accept full GitHub URLs
    if url.startswith('https://github.com/'):
        if not url.endswith('.git'):
            url = url.rstrip('/') + '.git'
        return url
    
    # Accept git protocol (convert to https)
    if url.startswith('git@github.com:'):
        repo = url.replace('git@github.com:', '').replace('.git', '')
        return f"https://github.com/{repo}.git"
    
    raise ValidationError(
        f"Invalid repository URL: {url}. "
        "Use: https://github.com/owner/repo, owner/repo, or git@github.com:owner/repo"
    )


def validate_branch_name(branch: str) -> str:
    """
    Validate Git branch name.
    
    Args:
        branch: Branch name
        
    Returns:
        Validated branch name
        
    Raises:
        ValidationError: If branch name is invalid
    """
    branch = validate_string_input(branch, "branch", min_length=1, max_length=255)
    
    # Git branch name validation
    invalid_chars = ['..', '~', '^', ':', '?', '*', '[', '\\']
    for char_seq in invalid_chars:
        if char_seq in branch:
            raise ValidationError(
                f"Branch name contains invalid character sequence: {char_seq}"
            )
    
    return branch


def validate_file_path(path: str, base_dir: str = None) -> str:
    """
    Validate file path to prevent directory traversal attacks.
    
    Args:
        path: File path to validate
        base_dir: Base directory to validate against (optional)
        
    Returns:
        Validated path
        
    Raises:
        ValidationError: If path is invalid or attempts traversal
    """
    path = validate_string_input(path, "file_path", min_length=1, max_length=1000)
    
    # Prevent absolute paths
    if os.path.isabs(path):
        raise ValidationError("Absolute paths are not allowed")
    
    # Prevent directory traversal
    normalized = os.path.normpath(path)
    if normalized.startswith('..'):
        raise ValidationError("Directory traversal not allowed (..) in path")
    
    # Validate against base directory if provided
    if base_dir:
        full_path = os.path.normpath(os.path.join(base_dir, path))
        base_normalized = os.path.normpath(os.path.abspath(base_dir))
        
        if not full_path.startswith(base_normalized):
            raise ValidationError(
                f"Path {path} escapes base directory {base_dir}"
            )
    
    return path


# ============================================================================
# GOOGLE OAUTH UTILITIES
# ============================================================================

class GoogleOAuthConfig:
    """Configuration for Google OAuth 2.0"""
    
    def __init__(self):
        """Initialize Google OAuth configuration from environment"""
        try:
            self.client_id = get_secure_api_key('GOOGLE_OAUTH_CLIENT_ID')
            self.client_secret = get_secure_api_key('GOOGLE_OAUTH_CLIENT_SECRET')
            self.redirect_uri = os.getenv(
                'GOOGLE_OAUTH_REDIRECT_URI',
                'http://localhost:8080/callback'
            )
            self.scopes = [
                'https://www.googleapis.com/auth/drive',
                'https://www.googleapis.com/auth/drive.file'
            ]
            self.auth_uri = 'https://accounts.google.com/o/oauth2/v2/auth'
            self.token_uri = 'https://oauth2.googleapis.com/token'
        except SecurityError as e:
            logger.warning(f"Google OAuth not configured: {e}")
            self.client_id = None
            self.client_secret = None
    
    def is_configured(self) -> bool:
        """Check if Google OAuth is properly configured"""
        return bool(self.client_id and self.client_secret)
    
    def get_authorization_url(self, state: str = None) -> str:
        """
        Generate Google OAuth authorization URL.
        
        Args:
            state: CSRF protection state token
            
        Returns:
            Authorization URL
            
        Raises:
            SecurityError: If OAuth is not configured
        """
        if not self.is_configured():
            raise SecurityError("Google OAuth is not configured")
        
        import urllib.parse
        
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': ' '.join(self.scopes),
            'access_type': 'offline',
            'prompt': 'consent'
        }
        
        if state:
            params['state'] = state
        
        query_string = urllib.parse.urlencode(params)
        return f"{self.auth_uri}?{query_string}"


def validate_oauth_code(code: str) -> str:
    """
    Validate OAuth authorization code.
    
    Args:
        code: Authorization code from OAuth provider
        
    Returns:
        Validated code
        
    Raises:
        ValidationError: If code is invalid
    """
    code = validate_string_input(
        code,
        "oauth_code",
        min_length=10,
        max_length=500,
        allowed_chars=r"a-zA-Z0-9\-_"
    )
    return code


def validate_oauth_state(state: str) -> str:
    """
    Validate OAuth state parameter (CSRF protection).
    
    Args:
        state: State token
        
    Returns:
        Validated state
        
    Raises:
        ValidationError: If state is invalid
    """
    state = validate_string_input(
        state,
        "oauth_state",
        min_length=20,
        max_length=500,
        allowed_chars=r"a-zA-Z0-9\-_"
    )
    return state
