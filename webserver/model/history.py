from sqlalchemy import Column, Integer, JSON
from .base import Base

class History(Base):
	__tablename__ = 'history'

	id      = Column(Integer, primary_key=True)
	data      = Column(JSON)
