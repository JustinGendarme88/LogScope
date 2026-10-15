# LogScope

LogScope is a REST API for importing and analyzing server log files.

It parses log entries, calculates useful HTTP statistics, stores analysis
results in SQLite, and exports results in JSON or CSV format.

## Features

- Upload `.log` and `.txt` files
- Validate file type, size, encoding, and content
- Parse server log entries
- Count total HTTP requests
- Calculate HTTP status code distribution
- Identify the most frequent errors
- Identify the most frequently used endpoints
- Calculate the average response time
- Store analysis history in SQLite
- Export analyses in JSON or CSV
- Interactive Swagger documentation
- Automated tests with Pytest

## Technologies

- Python
- FastAPI
- Pandas
- SQLAlchemy
- SQLite
- Pytest
- Swagger/OpenAPI

## Supported log format

Each line must follow this format:

```text
127.0.0.1 - - [18/Sep/2026:10:00:00 +0000] "GET /api/users HTTP/1.1" 200 512 125.5
```

The fields represent:

```text
IP - - [timestamp] "HTTP method endpoint protocol" status size response_time_ms
```

## Installation

Clone the repository and enter the project directory:

```bash
git clone <repository-url>
cd LogScope
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

## Running the API

Start the development server:

```bash
uvicorn app.main:app --reload
```

The API is available at:

```text
http://127.0.0.1:8000
```

Swagger documentation is available at:

```text
http://127.0.0.1:8000/docs
```

## API endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/logs/upload` | Upload and analyze a log file |
| `GET` | `/logs/analyses` | List saved analyses |
| `GET` | `/logs/analyses/{analysis_id}` | Retrieve one saved analysis |
| `GET` | `/logs/analyses/{analysis_id}/export/json` | Export an analysis as JSON |
| `GET` | `/logs/analyses/{analysis_id}/export/csv` | Export an analysis as CSV |

## Running the tests

```bash
pytest -v
```

## Project structure

```text
LogScope/
├── app/
│   ├── routers/
│   │   └── logs.py
│   ├── services/
│   │   ├── exporter.py
│   │   ├── log_analyzer.py
│   │   └── log_parser.py
│   ├── database.py
│   ├── main.py
│   └── models.py
├── tests/
│   ├── test_exporter.py
│   ├── test_log_analyzer.py
│   └── test_log_parser.py
├── requirements.txt
└── README.md
```

## Error handling

The API returns appropriate HTTP errors for:

- Empty files
- Unsupported file extensions
- Files larger than 5 MB
- Invalid UTF-8 encoding
- Files without valid log entries
- Analyses that do not exist