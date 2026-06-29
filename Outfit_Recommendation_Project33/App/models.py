from pydantic import BaseModel 
from typing import Optional
from App.database import Base
from py.recognition_module import top_list, bottom_list, foot_list
from pydantic import BaseModel
from typing import Optional
class ItemResponse(BaseModel):
    id: int
    type : str
    season: str
    usage : str
    gender: str
    image_url :str
    

class EditItem(BaseModel):
    type: Optional[str] = None   
    gender: Optional[str] = None
    color: Optional[str] = None
    season: Optional[str] = None
    usage: Optional[str] = None



class ClosetEditItem(BaseModel):
    gender: Optional[str] = None
    season: Optional[str] = None
    color: Optional[str] = None
    usage: Optional[str] = None
    type: Optional[str] = None

class AddToSession(BaseModel):
    user_id: str
    source: str  
    public_id: Optional[str] = None  
    
CATEGORY_LISTS = {
    "top": top_list,
    "bottom": bottom_list,
    "foot": foot_list,
}

from App.database import Base, engine
from sqlalchemy import Column, String

class UserPhoto(Base):
    __tablename__ = "user_photos"

    user_id = Column(String, primary_key=True)
    public_id = Column(String)
    image_url = Column(String)

