from fastapi import FastAPI
from database import engine, Base, SessionLocal
from parser import load_all_products
from crud import create_or_update_product
from crud import get_products, get_product_with_history
from fastapi import Query
from crud import get_analytics

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

@app.get("/products")
def list_products(
    min_price: float = Query(None),
    max_price: float = Query(None),
    category: str = Query(None)
):
    db = SessionLocal()
    products = get_products(db, min_price, max_price, category)
    db.close()

    return products


@app.get("/product/{product_id}")
def get_product(product_id: int):
    db = SessionLocal()
    result = get_product_with_history(db, product_id)
    db.close()

    if not result:
        return {"error": "Product not found"}

    return result


@app.get("/analytics")
def analytics():
    db = SessionLocal()
    result = get_analytics(db)
    db.close()
    return result