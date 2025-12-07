from pydantic import BaseModel

# Для джерел
class SourceCreate(BaseModel):
    name: str
    url: str

class SourceRead(BaseModel):
    id: int
    name: str
    url: str

    class Config:
        orm_mode = True

# Для товарів
class ItemCreate(BaseModel):
    price: float
    link: str
    source_id: int

class ItemRead(BaseModel):
    id: int
    price: float
    link: str
    source_id: int

    class Config:
        orm_mode = True
