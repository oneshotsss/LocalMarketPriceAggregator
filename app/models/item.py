from sqlalchemy import Column, String, Integer, Float, ForeignKey
from app.models.base_class import Base

class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True, index = True)
    price = Column(Float)
    link = Column(String)
    source_id = Column(Integer, ForeignKey('source.id'))