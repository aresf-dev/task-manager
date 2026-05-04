from pydantic import BaseModel
from typing import Optional

class TaskCreate(BaseModel):
    title: str
    description: str = ""
    due_date: Optional[str] = None
    priority: str = "medium"

class TaskResponse(TaskCreate):
    id: int
    completed: bool

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str