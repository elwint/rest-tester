from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from model import Base

engine = create_engine('postgres://postgres@localhost/test', echo=False)
Base.metadata.create_all(engine)

session = sessionmaker(bind=engine, autocommit=True)()
""":type: sqlalchemy.orm.Session"""
