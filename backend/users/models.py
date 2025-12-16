from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

# Helper to convert MongoDB ObjectId → string
class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        return str(v)


from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class User(BaseModel):
    id: Optional[str] = Field(alias="_id")

    name: Optional[str] = None
    email: Optional[str] = None
    password_hash: Optional[str] = None

    google_id: Optional[str] = None
    avatar: Optional[str] = None

    created_at: Optional[datetime] = None
    # Use default_factory to avoid shared mutable defaults
    favourites: List[str] = Field(default_factory=list)
    bag: List[str] = Field(default_factory=list)

    class Config:
        populate_by_name = True



class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str
