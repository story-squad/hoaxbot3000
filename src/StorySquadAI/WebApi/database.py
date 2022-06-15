import sqlalchemy.util
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

path_env = os.getenv("DATABASE_FILE")
SQLALCHEMY_DATABASE_URL = "sqlite:///" + path_env
# sqlite:///C:\\Users\\Username\\AppData\\Roaming\\Appname\\mydatabase.db

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()