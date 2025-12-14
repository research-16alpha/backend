from pydantic import BaseModel, EmailStr

class ContactForm(BaseModel):
    email: EmailStr
    message: str
