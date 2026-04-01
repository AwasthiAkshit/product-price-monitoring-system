from fastapi import FastAPI, Depends, HTTPException, Security, Query
from fastapi.security.api_key import APIKeyHeader
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base, SessionLocal
from parser import load_all_products_async
from crud import create_or_update_product, get_products, get_product_with_history, get_analytics
from models import APIUser

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

# Pre-populate our database with a test API key for the internship evaluation
def ensure_dummy_api_key():
    db = SessionLocal()
    if db.query(APIUser).count() == 0:
        db.add(APIUser(api_key="secret-token-123"))
        db.commit()
    db.close()

ensure_dummy_api_key()

# Setup explicit API Key Authentication Requirement
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)

def verify_api_key(api_key: str = Security(api_key_header)):
    db = SessionLocal()
    user = db.query(APIUser).filter(APIUser.api_key == api_key).first()
    if not user:
        db.close()
        raise HTTPException(
            status_code=403, 
            detail="Forbidden: Invalid or missing X-API-Key header. (Use secret-token-123)"
        )
    
    # Requirement: "track their usage per request"
    user.usage_count += 1
    db.commit()
    db.close()
    return user


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return {}


@app.get("/")
def root():
    return {"message": "API is running. All other endpoints require X-API-Key header authentication."}


@app.get("/refresh")
async def refresh(user: APIUser = Depends(verify_api_key)):
    db = SessionLocal()
    # Now uses the Async simulated data fetcher!
    products = await load_all_products_async()

    result = {
        "created": 0,
        "updated": 0,
        "no_change": 0,
        "price_changes": []
    }

    for p in products:
        status = create_or_update_product(db, p)
        if isinstance(status, dict):
            result["price_changes"].append({
                "name": status["name"],
                "old_price": status["old_price"],
                "new_price": status["new_price"]
            })
            result[status["status"]] += 1
        else:
            result[status] += 1

    db.close()
    return result


@app.get("/products")
def list_products(
    min_price: float = Query(None),
    max_price: float = Query(None),
    category: str = Query(None),
    user: APIUser = Depends(verify_api_key)
):
    db = SessionLocal()
    products = get_products(db, min_price, max_price, category)
    db.close()

    return products


@app.get("/product")
def get_product_redirect():
    return RedirectResponse(url="/products")


@app.get("/product/{product_id}")
def get_product(product_id: int, user: APIUser = Depends(verify_api_key)):
    db = SessionLocal()
    result = get_product_with_history(db, product_id)
    db.close()

    if not result:
        return {"error": "Product not found"}

    return result


@app.get("/analytics")
def analytics(user: APIUser = Depends(verify_api_key)):
    db = SessionLocal()
    result = get_analytics(db)
    db.close()
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)