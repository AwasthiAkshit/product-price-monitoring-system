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
