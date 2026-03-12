"""
Security Module — Production Security
=======================================
1. Ticker Blacklist — Dangerous/invalid inputs block karo
2. Input Sanitization — Clean & validate all inputs
3. Rate Limiting helpers
4. Security event logging
"""
import re
import logging
from django.core.cache import cache

logger = logging.getLogger('security')

# ============================================================
# TICKER BLACKLIST — Ye tickers dangerous ya invalid hain
# ============================================================
BLACKLISTED_TICKERS = {
    # SQL injection attempts
    "DROP", "SELECT", "INSERT", "DELETE", "UPDATE", "UNION",
    "OR", "AND", "WHERE", "FROM", "TABLE",
    # Script injection
    "SCRIPT", "ALERT", "ONCLICK", "ONERROR",
    # Known test/fake tickers
    "TEST", "HACK", "EVIL", "NULL", "NONE",
    # Empty/whitespace handled separately
}

# Valid ticker pattern: 1-5 uppercase letters, optional . or - for markets
VALID_TICKER_PATTERN = re.compile(r'^[A-Z]{1,5}([.\-][A-Z]{1,3})?$')

# Maximum requests per IP per hour
RATE_LIMIT_PER_HOUR = 20
RATE_LIMIT_PER_MINUTE = 5


def validate_ticker(ticker: str) -> tuple[bool, str]:
    """
    Ticker validate karo.
    Returns: (is_valid: bool, error_message: str)
    """
    if not ticker:
        return False, "Ticker empty hai!"

    ticker = ticker.upper().strip()

    # Length check
    if len(ticker) < 1 or len(ticker) > 10:
        return False, f"Ticker '{ticker}' invalid length! 1-10 characters allowed."

    # Blacklist check
    if ticker in BLACKLISTED_TICKERS:
        logger.warning(f"SECURITY: Blacklisted ticker attempted: {ticker}")
        return False, f"Ticker '{ticker}' is not allowed."

    # Pattern check
    if not VALID_TICKER_PATTERN.match(ticker):
        logger.warning(f"SECURITY: Invalid ticker pattern: {ticker}")
        return False, f"Ticker '{ticker}' invalid format! Only letters allowed (e.g., AAPL, GOOGL)."

    return True, ""


def check_rate_limit(identifier: str, limit_type: str = 'hour') -> tuple[bool, int]:
    """
    Rate limit check karo.
    Returns: (is_allowed: bool, remaining_requests: int)
    """
    if limit_type == 'minute':
        cache_key = f"rate_limit_min:{identifier}"
        limit = RATE_LIMIT_PER_MINUTE
        timeout = 60
    else:
        cache_key = f"rate_limit_hour:{identifier}"
        limit = RATE_LIMIT_PER_HOUR
        timeout = 3600

    current = cache.get(cache_key, 0)

    if current >= limit:
        logger.warning(f"RATE_LIMIT: {identifier} exceeded {limit_type} limit")
        return False, 0

    # Increment count
    try:
        cache.set(cache_key, current + 1, timeout)
    except Exception:
        pass  # Cache fail hone pe block mat karo

    return True, limit - current - 1


def get_client_ip(request) -> str:
    """Real client IP lo (proxy ke peeche se bhi)"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', 'unknown')


def log_security_event(event_type: str, details: dict, request=None):
    """Security events structured log karo"""
    log_data = {
        "event": event_type,
        **details,
    }
    if request:
        log_data["ip"] = get_client_ip(request)
        log_data["user"] = str(request.user) if request.user.is_authenticated else "anonymous"
        log_data["path"] = request.path
        log_data["method"] = request.method

    logger.warning(f"SECURITY_EVENT | {log_data}")
