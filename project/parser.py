# parser.py
import os
import json

DATA_FOLDER = "data/1stdibs"


def parse_1stdibs(data):
    return {
        "external_id": data.get("product_url"),
        "name": data.get("model"),
        "brand": data.get("brand"),
        "category": data.get("category") or "belt",
        "price": data.get("price"),
        "source": "1stdibs"
    }


def load_all_products():
    products = []

    for file_name in os.listdir(DATA_FOLDER):
        file_path = os.path.join(DATA_FOLDER, file_name)

        if file_path.endswith(".json"):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                parsed = parse_1stdibs(data)
                products.append(parsed)

    return products
