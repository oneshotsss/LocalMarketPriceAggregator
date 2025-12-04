from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import engine, SessionLocal
from app.models.base_class import Base
from app import models

app = FastAPI()

@app.on_event('startup')
def startup():
    Base.metadata.create_all(bind=engine)

@app.get('/')
def root():
    return {'status': "ok"}

# Залежність для DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post('/products')
def create_product(name: str, price: float, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.name == name).first()
    if db_product:
        raise HTTPException(status_code=400, detail="Product already exists")
    new_product = models.Product(name=name, price=price)
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return {"id": new_product.id, "name": new_product.name, "price": new_product.price}

@app.get('/products')
def read_products(db: Session = Depends(get_db)):
    products = db.query(models.Product).all()
    return [{"id": p.id, "name": p.name, "price": p.price} for p in products]

@app.put('/products/{product_id}')
def update_product(product_id: int, name: str, price: float, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).get(product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    db_product.name = name
    db_product.price = price
    db.commit()
    db.refresh(db_product)
    return {"id": db_product.id, "name": db_product.name, "price": db_product.price}

@app.delete('/products/{product_id}')
def delete_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).get(product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(db_product)
    db.commit()
    return {"detail": "Product deleted"}
