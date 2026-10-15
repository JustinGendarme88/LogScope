import pytest

from app.services.log_analyzer import analyze_logs


def test_analyze_logs():
    entries = [
        {
            "status_code": 200,
            "endpoint": "/api/users",
            "response_time_ms": 100.0,
        },
        {
            "status_code": 404,
            "endpoint": "/api/users",
            "response_time_ms": 200.0,
        },
        {
            "status_code": 500,
            "endpoint": "/api/login",
            "response_time_ms": 300.0,
        },
        {
            "status_code": 500,
            "endpoint": "/api/login",
            "response_time_ms": None,
        },
    ]

    statistics = analyze_logs(entries)

    assert statistics["total_requests"] == 4

    assert statistics["status_codes"] == {
        "200": 1,
        "404": 1,
        "500": 2,
    }

    assert statistics["top_errors"][0] == {
        "status_code": 500,
        "count": 2,
    }

    assert statistics["top_endpoints"] == [
        {
            "endpoint": "/api/users",
            "count": 2,
        },
        {
            "endpoint": "/api/login",
            "count": 2,
        },
    ]

    assert statistics["average_response_time_ms"] == 200.0
    assert statistics["requests_with_response_time"] == 3


def test_analyze_empty_logs():
    with pytest.raises(
        ValueError,
        match="At least one valid log entry is required.",
    ):
        analyze_logs([])