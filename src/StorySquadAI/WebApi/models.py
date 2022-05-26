from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from StorySquadAI.WebApi.database import Base


class ResponseRecord(Base):
    __tablename__ = "responses"
    id = Column(Integer, primary_key=True, index=True)
    response = Column(String, unique=True, index=True)
    is_bot =  Column(Boolean, unique=True, index=True)


