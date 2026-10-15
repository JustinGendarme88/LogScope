import csv
import json
from io import StringIO

from app.services.exporter import (
    create_csv_export,
    create_json_export,
)


SAMPLE_ANALYSIS = {
    "id": 1,
    "filename": "test.log",
    "size_bytes": 341,
    "parsed_entries": 3,
    "invalid_lines": 1,
    "total_requests": 3,
    "status_codes": {
        "200": 1,
        "201": 1,
        "500": 1,
    },
    "top_errors": [
        {
            "status_code": 500,
            "count": 1,
        }
    ],
    "top_endpoints": [
        {
            "endpoint": "/api/users",
            "count": 2,
        }
    ],
    "average_response_time_ms": 281.92,
    "requests_with_response_time": 3,
    "created_at": "2026-09-19T10:57:02",
}


def test_create_json_export():
    exported_content = create_json_export(SAMPLE_ANALYSIS)
    exported_data = json.loads(exported_content)

    assert exported_data == SAMPLE_ANALYSIS
    assert exported_data["filename"] == "test.log"
    assert exported_data["status_codes"]["500"] == 1


def test_create_csv_export():
    exported_content = create_csv_export(SAMPLE_ANALYSIS)

    reader = csv.DictReader(StringIO(exported_content))
    rows = list(reader)

    assert len(rows) == 1
    assert rows[0]["filename"] == "test.log"
    assert rows[0]["total_requests"] == "3"

    status_codes = json.loads(rows[0]["status_codes"])
    top_errors = json.loads(rows[0]["top_errors"])

    assert status_codes["500"] == 1
    assert top_errors[0]["status_code"] == 500