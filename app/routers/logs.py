from pathlib import Path
from typing import Any, Literal

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Response,
    UploadFile,
    status,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Analysis
from app.services.exporter import create_csv_export, create_json_export
from app.services.log_analyzer import analyze_logs
from app.services.log_parser import parse_log_content

router = APIRouter(prefix="/logs", tags=["Logs"])

ALLOWED_EXTENSIONS = {".log", ".txt"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


def serialize_analysis(analysis: Analysis) -> dict[str, Any]:
    return {
        "id": analysis.id,
        "filename": analysis.filename,
        "size_bytes": analysis.size_bytes,
        "parsed_entries": analysis.parsed_entries,
        "invalid_lines": analysis.invalid_lines,
        "total_requests": analysis.total_requests,
        "status_codes": analysis.status_codes,
        "top_errors": analysis.top_errors,
        "top_endpoints": analysis.top_endpoints,
        "average_response_time_ms": analysis.average_response_time_ms,
        "requests_with_response_time": (
            analysis.requests_with_response_time
        ),
        "created_at": analysis.created_at.isoformat(),
    }


@router.post("/upload", status_code=status.HTTP_200_OK)
async def upload_log_file(
    file: UploadFile,
    database: Session = Depends(get_db),
):
    filename = file.filename

    if not filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file must have a filename.",
        )

    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only .log and .txt files are supported.",
        )

    content = await file.read()
    file_size = len(content)

    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is empty.",
        )

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="The uploaded file exceeds the 5 MB size limit.",
        )

    try:
        decoded_content = content.decode("utf-8")
    except UnicodeDecodeError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file must use UTF-8 encoding.",
        ) from error

    parsed_entries, invalid_lines = parse_log_content(decoded_content)

    if not parsed_entries:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="The file does not contain any valid log entries.",
        )

    statistics = analyze_logs(parsed_entries)

    analysis = Analysis(
        filename=filename,
        size_bytes=file_size,
        parsed_entries=len(parsed_entries),
        invalid_lines=invalid_lines,
        total_requests=statistics["total_requests"],
        status_codes=statistics["status_codes"],
        top_errors=statistics["top_errors"],
        top_endpoints=statistics["top_endpoints"],
        average_response_time_ms=(
            statistics["average_response_time_ms"]
        ),
        requests_with_response_time=(
            statistics["requests_with_response_time"]
        ),
    )

    database.add(analysis)
    database.commit()
    database.refresh(analysis)

    return {
        "message": "Log file analyzed and saved successfully.",
        "analysis_id": analysis.id,
        "filename": filename,
        "size_bytes": file_size,
        "parsed_entries": len(parsed_entries),
        "invalid_lines": invalid_lines,
        "statistics": statistics,
        "preview": parsed_entries[:5],
        "created_at": analysis.created_at.isoformat(),
    }


@router.get("/analyses")
def list_analyses(
    limit: int = Query(default=20, ge=1, le=100),
    database: Session = Depends(get_db),
):
    statement = (
        select(Analysis)
        .order_by(Analysis.id.desc())
        .limit(limit)
    )

    analyses = database.scalars(statement).all()

    return {
        "count": len(analyses),
        "analyses": [
            serialize_analysis(analysis)
            for analysis in analyses
        ],
    }


@router.get("/analyses/{analysis_id}")
def get_analysis(
    analysis_id: int,
    database: Session = Depends(get_db),
):
    analysis = database.get(Analysis, analysis_id)

    if analysis is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found.",
        )

    return serialize_analysis(analysis)


@router.get("/analyses/{analysis_id}/export/{export_format}")
def export_analysis(
    analysis_id: int,
    export_format: Literal["json", "csv"],
    database: Session = Depends(get_db),
):
    analysis = database.get(Analysis, analysis_id)

    if analysis is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found.",
        )

    export_data = serialize_analysis(analysis)

    if export_format == "json":
        content = create_json_export(export_data)
        media_type = "application/json"
        filename = f"analysis_{analysis_id}.json"
    else:
        content = create_csv_export(export_data)
        media_type = "text/csv"
        filename = f"analysis_{analysis_id}.csv"

    return Response(
        content=content,
        media_type=media_type,
        headers={
            "Content-Disposition": (
                f'attachment; filename="{filename}"'
            )
        },
    )