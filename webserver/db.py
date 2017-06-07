from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from model import Base

engine = create_engine('postgres://postgres@localhost/test')
Base.metadata.create_all(engine)

session = sessionmaker(bind=engine)()
""":type: sqlalchemy.orm.Session"""
