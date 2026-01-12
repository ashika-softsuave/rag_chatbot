from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.db.base import Base

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    # 🔗 User ↔ Conversation
    user = relationship("User", back_populates="conversations")

    # 🔗 Conversation ↔ Messages  ✅ ADD THIS
    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete"
    )
