from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.models.base_class import Base
from app.models.item import Item
from app.models.source import Source
from app import schemas

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

app = FastAPI(title="Local Market Price Aggregator")

# --- Створюємо таблиці при старті ---
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

# --- DB dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- SOURCES ---
@app.post("/sources", response_model=schemas.SourceRead)
def create_source(source: schemas.SourceCreate, db: Session = Depends(get_db)):
    db_source = Source(**source.dict())
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return db_source

@app.get("/sources", response_model=list[schemas.SourceRead])
def read_sources(db: Session = Depends(get_db)):
    return db.query(Source).all()

# --- ITEMS ---
@app.get("/items", response_model=list[schemas.ItemRead])
def read_items(source_id: int = None, db: Session = Depends(get_db)):
    query = db.query(Item)
    if source_id:
        query = query.filter(Item.source_id == source_id)
    return query.all()

# --- PARSER однієї сторінки ---
def parse_page(url: str, source_id: int, db: Session):
    r = requests.get(url)
    if r.status_code != 200:
        return 0
    soup = BeautifulSoup(r.text, "html.parser")
    products = soup.select("article.product_pod")
    count = 0
    for p in products:
        try:
            link_tag = p.select_one("h3 a")
            link = urljoin(url, link_tag["href"])  # абсолютне посилання
            price_str = p.select_one(".price_color").text.strip()  # "£53.74"
            price = float(price_str[1:])
        except:
            continue
        db_item = Item(price=price, link=link, source_id=source_id)
        db.add(db_item)
        count += 1
    db.commit()
    return count

# --- PARSER всіх сторінок ---
@app.post("/parse_all/{source_id}")
def parse_all_pages(source_id: int, db: Session = Depends(get_db)):
    source = db.query(Source).get(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    base_url = source.url
    page_url = base_url
    total_count = 0

    while page_url:
        count = parse_page(page_url, source_id, db)
        total_count += count
        # перевіряємо наявність "next" сторінки
        r = requests.get(page_url)
        soup = BeautifulSoup(r.text, "html.parser")
        next_tag = soup.select_one(".next a")
        if next_tag:
            page_url = urljoin(base_url, next_tag["href"])
        else:
            page_url = None

    return {"status": "ok", "total_parsed_items": total_count}
