# crud.py
from sqlalchemy.orm import Session
from models import Product, PriceHistory


def create_or_update_product(db: Session, product_data: dict):
    existing = db.query(Product).filter(
        Product.external_id == product_data["external_id"]
    ).first()

    # NEW PRODUCT
    if not existing:
        new_product = Product(
            external_id=product_data["external_id"],
            name=product_data["name"],
            brand=product_data["brand"],
            category=product_data["category"],
            source=product_data["source"],
            current_price=product_data["price"]
        )
        db.add(new_product)
        db.commit()
        db.refresh(new_product)

        # add initial price history
        history = PriceHistory(
            product_id=new_product.id,
            price=new_product.current_price
        )
        db.add(history)
        db.commit()

        return "created"

    # EXISTING PRODUCT → check price change
    if existing.current_price != product_data["price"]:
        existing.current_price = product_data["price"]
        db.commit()

        history = PriceHistory(
            product_id=existing.id,
            price=existing.current_price
        )
        db.add(history)
        db.commit()

        return "updated"

    return "no_change"

def get_products(db: Session, min_price=None, max_price=None, category=None):
    query = db.query(Product)

    if min_price:
        query = query.filter(Product.current_price >= min_price)

    if max_price:
        query = query.filter(Product.current_price <= max_price)

    if category:
        query = query.filter(Product.category == category)

    return query.all()


def get_product_with_history(db: Session, product_id: int):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        return None

    history = db.query(PriceHistory).filter(
        PriceHistory.product_id == product_id
    ).all()

    return {
        "product": product,
        "history": history
    }

from sqlalchemy import func

def get_analytics(db: Session):
    total_products = db.query(func.count(Product.id)).scalar()

    avg_price = db.query(func.avg(Product.current_price)).scalar()

    by_source = db.query(
        Product.source,
        func.count(Product.id)
    ).group_by(Product.source).all()

    by_category = db.query(
        Product.category,
        func.avg(Product.current_price)
    ).group_by(Product.category).all()

    return {
        "total_products": total_products,
        "average_price": avg_price,
        "products_by_source": dict(by_source),
        "avg_price_by_category": dict(by_category)
    }   
