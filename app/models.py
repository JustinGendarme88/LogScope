from datetime import datetime, timezone
from typing import Any

from sqlalchemy import JSON, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )
    filename: Mapped[str] = mapped_column(String, nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    parsed_entries: Mapped[int] = mapped_column(Integer, nullable=False)
    invalid_lines: Mapped[int] = mapped_column(Integer, nullable=False)
    total_requests: Mapped[int] = mapped_column(Integer, nullable=False)

    status_codes: Mapped[dict[str, int]] = mapped_column(
        JSON,
        nullable=False,
    )
    top_errors: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON,
        nullable=False,
    )
    top_endpoints: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON,
        nullable=False,
    )

    average_response_time_ms: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    requests_with_response_time: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )