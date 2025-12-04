
from sqlalchemy import create_engine, text

engine = create_engine("postgresql+psycopg2://postgres:1839@localhost:5433/mydb")

with engine.connect() as conn:
    result = conn.execute(text("SELECT version();"))
    print(result.fetchone())

