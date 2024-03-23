from pydantic import BaseModel

class User(BaseModel):
    user: str  
    
class Ratio(BaseModel):
    ratio: float 