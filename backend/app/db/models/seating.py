from sqlalchemy import Column, Integer, String, ForeignKey
from backend.app.db.base import Base

class Seating(Base):
    __tablename__ = "seating"

    id = Column(Integer, primary_key=True, index=True)
    row_number = Column(Integer, nullable=False)
    column_number = Column(Integer, nullable=False)
    tech_stack = Column(String, nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
