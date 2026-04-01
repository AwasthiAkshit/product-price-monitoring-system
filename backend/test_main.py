import pytest
from fastapi.testclient import TestClient
from main import app, SessionLocal, engine, Base
from models import APIUser

# Ensure the clean DB exists
Base.metadata.create_all(bind=engine)
client = TestClient(app)

HEADERS = {"X-API-Key": "secret-token-123"}
BAD_HEADERS = {"X-API-Key": "obviously-wrong-key"}

# 1. Happy Path: Check Root Health
def test_root_is_healthy():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

# 2. Edge Case: Verify Security Auth Failure Missing Key
def test_refresh_missing_auth():
    response = client.get("/refresh")
    assert response.status_code == 403

# 3. Edge Case: Verify Security Auth Failure Bad Key
def test_refresh_bad_auth():
    response = client.get("/refresh", headers=BAD_HEADERS)
    assert response.status_code == 403

# 4. Happy Path: Refresh Valid Auth Core Functionality
def test_refresh_success():
    response = client.get("/refresh", headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert "updated" in data
    assert "created" in data
    assert "price_changes" in data

# 5. Happy Path: Fetch All Products
def test_list_products():
    response = client.get("/products", headers=HEADERS)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# 6. Edge Case: Fetch Products using Query Limiters
def test_list_products_with_filters():
    response = client.get("/products?min_price=10&max_price=100000", headers=HEADERS)
    assert response.status_code == 200

# 7. Edge Case: Request Out of Bounds ID gracefully handles
def test_get_invalid_product():
    response = client.get("/product/999999999", headers=HEADERS)
    assert response.status_code == 200
    assert response.json() == {"error": "Product not found"}

# 8. Happy Path: Confirm Analytics Outputs Correct Structure
def test_analytics():
    response = client.get("/analytics", headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert "total_products" in data
    assert "average_price" in data
