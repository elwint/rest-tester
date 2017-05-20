from sqlalchemy import Column, Integer, String, DateTime
from .base import Base
import datetime

class Token(Base):
	__tablename__ = 'token'

	user_id  = Column(Integer,     nullable=False)
	token    = Column(String(100), primary_key=True)
	created  = Column(DateTime,    nullable=False, default=datetime.datetime.utcnow)
