from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
import datetime
import uuid

Base = declarative_base()

class ApiKey(Base):
    __tablename__ = "api_keys"

    key = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    role = Column(String, nullable=False)  # e.g., "admin", "user"
    owner_email = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_used_at = Column(DateTime)
    active = Column(Boolean, default=True)
