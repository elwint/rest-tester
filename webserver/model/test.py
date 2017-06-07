from sqlalchemy import Column, Integer
from sqlalchemy.dialects.postgresql import JSON
from .base import Base

class Test(Base):
	__tablename__ = 'test'

	id      = Column(Integer, primary_key=True)
	data      = Column(JSON)
