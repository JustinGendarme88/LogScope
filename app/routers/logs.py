from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, status

from app.services.log_parser import parse_log_content

router = APIRouter(prefix="/logs", tags=["Logs"])

ALLOWED_EXTENSIONS = {".log", ".txt"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


@router.post("/upload", status_code=status.HTTP_200_OK)
async def upload_log_file(file: UploadFile):
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

    return {
        "message": "Log file parsed successfully.",
        "filename": filename,
        "size_bytes": file_size,
        "parsed_entries": len(parsed_entries),
        "invalid_lines": invalid_lines,
        "preview": parsed_entries[:5],
    }