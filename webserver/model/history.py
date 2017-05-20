from sqlalchemy import Column, Integer, String, DateTime, Boolean
from .base import Base

class History(Base):
	__tablename__ = 'history'

	test_id = Column(Integer,  nullable=False)
	time    = Column(DateTime, nullable=False)
	ok      = Column(Boolean,  nullable=False)
	elapsed = Column(Integer,  nullable=False)
