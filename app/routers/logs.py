from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, status

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

    return {
        "message": "Log file uploaded successfully.",
        "filename": filename,
        "size_bytes": file_size,
    }