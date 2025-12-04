from sqlalchemy import Column, String, Integer
from app.models.base_class import Base

class Source(Base):
    __tablename__ = 'source'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    url = Column(String)