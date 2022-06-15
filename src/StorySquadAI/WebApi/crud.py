from sqlalchemy.orm import Session

from src.StorySquadAI.WebApi import schemas, models


def get_response(db: Session, id: int):
    return db.query(models.ResponseRecord).filter(models.ResponseRecord.id == id).first()


def get_responses(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.ResponseRecord).offset(skip).limit(limit).all()


def create_response(db: Session, record: schemas.ResponseRecord):
    db_ResponseRecord = models.ResponseRecord(
        response=record.response,
        is_bot=record.is_bot)
    db.add(db_ResponseRecord)
    db.commit()
    db.refresh(db_ResponseRecord)
    return db_ResponseRecord
