from pydantic import BaseModel
from uuid import UUID, uuid4

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class User(BaseModel):
    id: UUID | None = None # Use UUID as the ID type
    username: str
    password: str

    class Config:
        orm_mode = True
