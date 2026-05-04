from pydantic import BaseModel
from typing import Optional

class SComment(BaseModel):
    comment: Optional[str]= None