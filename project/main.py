from fastapi import FastAPI
from database import engine, Base, SessionLocal
from parser import load_all_products
from crud import create_or_update_product

app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "API is running"}


@app.get("/refresh")
def refresh():
    db = SessionLocal()
    products = load_all_products()

    result = {
        "created": 0,
        "updated": 0,
        "no_change": 0
    }

    for p in products:
        status = create_or_update_product(db, p)
        result[status] += 1

    db.close()
    return result