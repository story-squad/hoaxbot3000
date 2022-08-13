from typing import Optional
from pydantic import BaseModel
from typing import Literal

class ResponseRecord(BaseModel):
    id: int
    response: str
    is_bot:bool

class word_hoax_prompt(BaseModel):
    api_key: str
    prompt: str
    correct_definition: str
    bot_name: str
    # def_type can be one of: thing, movie, person
    def_type: Literal["thing", "movie", "person"]


