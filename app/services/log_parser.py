import re
from datetime import datetime
from typing import Any
from urllib.parse import urlsplit

LOG_PATTERN = re.compile(
    r'^(?P<ip>\S+) \S+ \S+ '
    r'\[(?P<timestamp>[^\]]+)\] '
    r'"(?P<method>[A-Z]+) (?P<target>\S+) '
    r'(?P<protocol>HTTP/\d(?:\.\d)?)" '
    r'(?P<status_code>\d{3}) '
    r'(?P<response_size>\d+|-)'
    r'(?P<extra>.*)$'
)

RESPONSE_TIME_PATTERN = re.compile(
    r"\s(?P<response_time_ms>\d+(?:\.\d+)?)\s*$"
)

TIMESTAMP_FORMAT = "%d/%b/%Y:%H:%M:%S %z"


def parse_log_line(line: str) -> dict[str, Any] | None:
    """Parse one Apache or Nginx log line."""

    match = LOG_PATTERN.match(line.strip())

    if not match:
        return None

    try:
        timestamp = datetime.strptime(
            match.group("timestamp"),
            TIMESTAMP_FORMAT,
        )
    except ValueError:
        return None

    target = match.group("target")
    endpoint = urlsplit(target).path or "/"

    response_size_value = match.group("response_size")
    response_size = (
        int(response_size_value)
        if response_size_value != "-"
        else None
    )

    extra = match.group("extra")
    response_time_match = RESPONSE_TIME_PATTERN.search(extra)

    response_time_ms = (
        float(response_time_match.group("response_time_ms"))
        if response_time_match
        else None
    )

    return {
        "ip_address": match.group("ip"),
        "timestamp": timestamp.isoformat(),
        "method": match.group("method"),
        "endpoint": endpoint,
        "protocol": match.group("protocol"),
        "status_code": int(match.group("status_code")),
        "response_size_bytes": response_size,
        "response_time_ms": response_time_ms,
    }


def parse_log_content(
    content: str,
) -> tuple[list[dict[str, Any]], int]:
    """Parse all non-empty lines and count invalid entries."""

    parsed_entries: list[dict[str, Any]] = []
    invalid_lines = 0

    for line in content.splitlines():
        if not line.strip():
            continue

        parsed_line = parse_log_line(line)

        if parsed_line is None:
            invalid_lines += 1
            continue

        parsed_entries.append(parsed_line)

    return parsed_entries, invalid_lines