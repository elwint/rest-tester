from sqlalchemy import Column, Integer, String
from .base import Base

class User(Base):
	__tablename__ = 'user'

	id       = Column(Integer,     primary_key=True)
	name     = Column(String(100), nullable=False)
	password = Column(String(600),  nullable=False) # TODO: Fix this/login
