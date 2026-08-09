from sqlalchemy import Column, Integer, String, Text, Float, Boolean
from pgvector.sqlalchemy import Vector

from app.db.base import Base


class Policy(Base):

    __tablename__ = "policies"

    id = Column(Integer, primary_key=True)

    category = Column(
        String(100),
        nullable=False
    )

    description = Column(
        Text,
        nullable=False
    )

    severity = Column(
        String(20),
        nullable=False
    )

    threshold = Column(
        Float,
        default=0.85
    )

    action = Column(
        String(20),
        default="BLOCK"
    )

    example = Column(
        Text,
        nullable=False
    )

    embedding = Column(
        Vector(384),
        nullable=False
    )

    enabled = Column(
        Boolean,
        default=True
    )