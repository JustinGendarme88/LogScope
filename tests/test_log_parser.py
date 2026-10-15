from app.services.log_parser import parse_log_content


def test_parse_valid_log_lines():
    content = (
        '127.0.0.1 - - [18/Sep/2026:10:00:00 +0000] '
        '"GET /api/users HTTP/1.1" 200 512 125.5\n'
        '192.168.1.15 - - [18/Sep/2026:10:01:00 +0000] '
        '"POST /api/login HTTP/1.1" 201 128 240\n'
    )

    entries, invalid_lines = parse_log_content(content)

    assert len(entries) == 2
    assert invalid_lines == 0

    assert entries[0]["ip_address"] == "127.0.0.1"
    assert entries[0]["method"] == "GET"
    assert entries[0]["endpoint"] == "/api/users"
    assert entries[0]["status_code"] == 200
    assert entries[0]["response_size_bytes"] == 512
    assert entries[0]["response_time_ms"] == 125.5


def test_parse_invalid_log_line():
    content = (
        '127.0.0.1 - - [18/Sep/2026:10:00:00 +0000] '
        '"GET /api/users HTTP/1.1" 200 512 125.5\n'
        "This is not a valid log line\n"
    )

    entries, invalid_lines = parse_log_content(content)

    assert len(entries) == 1
    assert invalid_lines == 1


def test_parse_empty_content():
    entries, invalid_lines = parse_log_content("")

    assert entries == []
    assert invalid_lines == 0