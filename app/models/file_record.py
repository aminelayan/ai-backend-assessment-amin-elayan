from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class FileRecord(Base):
    __tablename__ = "file_records"

    filename = Column(String, primary_key=True)
    file_hash = Column(String, nullable=False)
    processed_at = Column(DateTime, default=datetime.datetime.utcnow)
    tokens_estimate = Column(Integer)
