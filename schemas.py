from typing import Optional
from pydantic import BaseModel


class ResponseRecord(BaseModel):
    id: int
    response: str
    is_bot:bool


