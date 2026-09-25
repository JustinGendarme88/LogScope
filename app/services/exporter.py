import csv
import json
from io import StringIO
from typing import Any


def create_json_export(data: dict[str, Any]) -> str:
    """Convert an analysis into formatted JSON."""

    return json.dumps(
        data,
        indent=2,
        ensure_ascii=False,
    )


def create_csv_export(data: dict[str, Any]) -> str:
    """Convert an analysis into a single CSV row."""

    csv_data = data.copy()

    for field in ("status_codes", "top_errors", "top_endpoints"):
        csv_data[field] = json.dumps(
            csv_data[field],
            ensure_ascii=False,
        )

    output = StringIO(newline="")

    writer = csv.DictWriter(
        output,
        fieldnames=csv_data.keys(),
    )
    writer.writeheader()
    writer.writerow(csv_data)

    return output.getvalue()