from pydantic import BaseModel

class TaskCreate(BaseModel):
    title: str
    description: str = ""

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