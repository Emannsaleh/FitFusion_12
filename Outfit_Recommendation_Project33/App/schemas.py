from pydantic import BaseModel, Field
class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str = Field(..., max_length=500) 
class LoginRequest(BaseModel):
    email: str
    password: str