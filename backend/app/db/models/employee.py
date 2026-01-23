from sqlalchemy import String, Float, DateTime
from sqlalchemy.sql import func
from backend.app.db.base import Base
from sqlalchemy import Integer
from sqlalchemy import Column, JSON
from sqlalchemy.ext.mutable import MutableDict

onboarding_state = Column(MutableDict.as_mutable(JSON), nullable=True)



class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String, nullable=True)
    tech_stack = Column(String, nullable=True)

    tenth_percentage = Column(Float, nullable=True)
    twelfth_percentage = Column(Float, nullable=True)

    eligibility_status = Column(String, nullable=True)  # selected / rejected

    # onboarding_state = Column(JSON, nullable=False, default={})

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    onboarding_state = Column(MutableDict.as_mutable(JSON), nullable=False)

