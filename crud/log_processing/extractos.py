import re
from typing import Optional

from schemas.log_analysis import ExtractedLogFields


def extract_log_level(raw_log: str) -> Optional[str]:
    normalized_log = raw_log.upper()

    match = re.search(
        r"\b(ERROR|WARN|WARNING|INFO|DEBUG|CRITICAL|FATAL|SEVERE)\b",
        normalized_log,
    )

    if not match:
        return None

    log_level = match.group(1)

    if log_level == "WARNING":
        return "WARN"

    if log_level in {"FATAL", "SEVERE"}:
        return "ERROR"

    return log_level


def extract_status_code(raw_log: str) -> Optional[int]:
    normalized_log = raw_log.upper()

    patterns = [
        r"\bSTATUS(?:_CODE)?\s*[:=]?\s*([1-5]\d{2})\b",
        r"\bHTTP\s*[:=]?\s*([1-5]\d{2})\b",
        r"\bCODE\s*[:=]?\s*([1-5]\d{2})\b",
        r"\bRETURNED\s+([1-5]\d{2})\b",
        r"\bRESPONSE\s*[:=]?\s*([1-5]\d{2})\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, normalized_log)
        if match:
            return int(match.group(1))

    return None


def extract_exception_type(raw_log: str) -> Optional[str]:
    patterns = [
        r"\bEXCEPTION\s*[:=]\s*([A-Z][a-zA-Z0-9_]*(?:Error|Exception|Timeout))\b",
        r"\bERROR\s*[:=]\s*([A-Z][a-zA-Z0-9_]*(?:Error|Exception|Timeout))\b",
        r"\bCAUSED BY\s+([A-Z][a-zA-Z0-9_]*(?:Error|Exception|Timeout))\b",
        r"\b[a-zA-Z_][\w.]*\.([A-Z][a-zA-Z0-9_]*(?:Error|Exception|Timeout))\b",
        r"\b([A-Z][a-zA-Z0-9_]*(?:Error|Exception|Timeout))\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, raw_log)
        if match:
            return match.group(1)

    normalized_log = raw_log.upper()

    hint_patterns = {
        "TimeoutError": r"\b(TIMEOUT|TIMED OUT|READ TIMEOUT|WRITE TIMEOUT)\b",
        "ConnectionRefusedError": r"\b(CONNECTION REFUSED|ECONNREFUSED)\b",
        "PermissionError": r"\b(PERMISSION DENIED|ACCESS DENIED|FORBIDDEN)\b",
        "AuthError": r"\b(UNAUTHORIZED|INVALID TOKEN|TOKEN EXPIRED)\b",
        "NotFoundError": r"\b(NOT FOUND)\b",
    }

    for exception_type, pattern in hint_patterns.items():
        if re.search(pattern, normalized_log):
            return exception_type

    return None


def extract_log_fields(raw_log: str) -> ExtractedLogFields:
    return ExtractedLogFields(
        log_level=extract_log_level(raw_log),
        status_code=extract_status_code(raw_log),
        exception_type=extract_exception_type(raw_log),
    )