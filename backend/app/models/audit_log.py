from datetime import datetime
from sqlalchemy import JSON, Column, DateTime, String

from app.db.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True)
    request_id = Column(String, index=True)
    username = Column(String)
    role = Column(String)
    department = Column(String)
    event_type = Column(String)
    event_data = Column(JSON)
    previous_hash = Column(String)
    current_hash = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)