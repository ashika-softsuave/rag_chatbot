from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, timedelta
from backend.app.db.base import Base

class OTP(Base):
    __tablename__ = "otps"

    id = Column(Integer, primary_key=True)
    email = Column(String, index=True)
    code = Column(String)
    expires_at = Column(DateTime)

    @staticmethod
    def expiry():
        return datetime.utcnow() + timedelta(minutes=10)
