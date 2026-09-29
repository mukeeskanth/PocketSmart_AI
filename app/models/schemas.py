from typing import List
from pydantic import BaseModel, Field

class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: str
    password: str = Field(min_length=6, max_length=128)

class LoginRequest(BaseModel):
    email: str
    password: str

class HomeRequest(BaseModel):
    budget: float = Field(gt=0)
    rooms: List[str] = Field(min_length=1)
    style: str = "Modern"
    items: str = ""
    city: str = ""

class PartyRequest(BaseModel):
    budget: float = Field(gt=0)
    guests: int = Field(gt=0, le=10000)
    event_type: str = "Birthday"
    venue: str = ""
    city: str = ""
    preferences: str = ""
