from pydantic import BaseModel, EmailStr
from typing import Optional, Dict


class OnboardingStartResponse(BaseModel):
    message: str
    step: str


class OnboardingNextRequest(BaseModel):
    user_input: str


class OnboardingNextResponse(BaseModel):
    message: str
    step: str
    completed: bool = False
