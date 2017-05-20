from sqlalchemy import Column, Integer, String, Boolean
from .base import Base

class Test(Base):
	__tablename__ = 'test'

	id      = Column(Integer,      primary_key=True)
	user_id = Column(Integer,      nullable=False)
	name    = Column(String(100),  nullable=False)
	last_ok = Column(Boolean)
	data    = Column(String(5000), nullable=False)
