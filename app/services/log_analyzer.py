from typing import Any

import pandas as pd


def analyze_logs(entries: list[dict[str, Any]]) -> dict[str, Any]:
    """Calculate statistics from parsed log entries."""

    if not entries:
        raise ValueError("At least one valid log entry is required.")

    frame = pd.DataFrame(entries)
    error_rows = frame[frame["status_code"] >= 400]

    status_codes = {
        str(code): int(count)
        for code, count in frame["status_code"].value_counts().sort_index().items()
    }

    top_errors = [
        {"status_code": int(code), "count": int(count)}
        for code, count in error_rows["status_code"].value_counts().head(5).items()
    ]

    top_endpoints = [
        {"endpoint": str(endpoint), "count": int(count)}
        for endpoint, count in frame["endpoint"].value_counts().head(5).items()
    ]

    response_times = frame["response_time_ms"].dropna()
    average_response_time_ms = (
        round(float(response_times.mean()), 2)
        if not response_times.empty
        else None
    )

    return {
        "total_requests": len(frame),
        "status_codes": status_codes,
        "top_errors": top_errors,
        "top_endpoints": top_endpoints,
        "average_response_time_ms": average_response_time_ms,
        "requests_with_response_time": len(response_times),
    }