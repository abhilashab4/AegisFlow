from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime
)

from datetime import datetime

from app.db.base import Base


class UsageLog(Base):

    __tablename__ = "usage_logs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    username = Column(
        String,
        nullable=False
    )

    role = Column(
        String,
        nullable=False
    )

    department = Column(
        String,
        nullable=False
    )

    model = Column(
        String,
        nullable=False
    )

    provider = Column(
        String,
        nullable=False
    )

    prompt_tokens = Column(
        Integer,
        default=0
    )

    completion_tokens = Column(
        Integer,
        default=0
    )

    total_tokens = Column(
        Integer,
        default=0
    )

    estimated_cost = Column(
        Float,
        default=0.0
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )