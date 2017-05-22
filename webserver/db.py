from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from model import Base

engine = create_engine('sqlite:///:memory:', echo=False)
Base.metadata.create_all(engine)

session = sessionmaker(bind=engine)()
""":type: sqlalchemy.orm.Session"""
