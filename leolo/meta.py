"""
Here is the connection to the database.
"""
import settings
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

engine = create_engine(settings.LEOLO_ENGINE, echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine, autoflush=True)

