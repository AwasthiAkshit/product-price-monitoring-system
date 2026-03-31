from fastapi import FastAPI
from database import engine, Base
from parser import load_all_products

app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "API is running"}


@app.get("/test-load")
def test_load():
    products = load_all_products()
    return {
        "count": len(products),
        "sample": products[:2]
    }