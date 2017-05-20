from sqlalchemy import Column, Integer, String
from .base import Base

class Group(Base):
	__tablename__ = 'group'

	user_id = Column(Integer,     nullable=False)
	name    = Column(String(100), nullable=False)
