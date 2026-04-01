# Product Price Monitoring System

## Overview
This is a Product Price Monitoring System built for the Entrupy Engineering Intern Assessment. It uses FastAPI for the backend, SQLite for data storage, and vanilla HTML/JS/CSS for a lightweight frontend dashboard. The system collects product data from local JSON samples (1stdibs, Grailed, Fashionphile), tracks price changes over time, and exposes an API for data access.

## How to Run

1. Open your terminal in the root project directory.
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the FastAPI server:
   ```bash
   cd backend
   python -m uvicorn main:app --reload
   ```
4. The API will run on `http://127.0.0.1:8000`. 
5. Open `frontend/index.html` in your web browser to view the dashboard.

## API Endpoints
*Note: All endpoints except the root require an `X-API-Key` header for authentication. A standard test key (`secret-token-123`) is pre-populated in the DB on startup.*

- **GET /refresh** - Asynchronously reads the JSON data folder, checks for price changes, and updates the database.
- **GET /products** - Returns a list of all products. Accepts query parameters for `min_price`, `max_price`, and `category`.
- **GET /product/{id}** - Returns details for a specific product along with its price history.
- **GET /analytics** - Returns aggregate totals and averages for the frontend dashboard.

## Design Decisions

**Async Data Fetching**
Since the initial data is provided locally as files, I simulated async network fetching using Python's native `asyncio`. I implemented an exponential backoff `try/except` loop to handle simulated failures. This meets the assignment requirement natively without needing external task queues like Celery.

**Notification of Price Changes**
Instead of attempting live webhooks that could timeout and block the main data fetching thread, I chose an Event-Driven Notification strategy. When a price change is detected by the scraper, it writes a new record directly into a `PriceEventLog` table. Downstream alerting systems can periodically poll this table. This ensures zero events are lost during network failures and the main fetcher is never bottlenecked waiting for an HTTP response.

**API Authentication & Tracking**
To track usage per request and authenticate consumers cleanly, I implemented a FastAPI dependency that checks for an `X-API-Key` header. Valid requests securely increment a `usage_count` field in the `api_users` table to track metrics.

**Scaling Price History (Millions of Rows)**
Currently, the database is normalized in SQLite. If the table scaled to millions of rows across 100+ data sources, the SQLite structure would bottleneck on write operations. To fix this, I would migrate the storage layer to a clustered PostgreSQL database and implement horizontal table partitioning, chunking the `PriceHistory` and `PriceEventLog` tables by `timestamp` and `product_id`.

## Known Limitations
- The current "scraper" module reads local `.json` files. In a true production environment, this would be replaced with actual async HTTP requests (using `httpx` or `aiohttp`) connected to rotating proxy networks.
- There is currently no web-based UI specifically dedicated to generating, revoking, or rotating API keys for users.
- The Event Log polling system would eventually need a way to mark events as "read" or "processed" once downstream alerts are successfully distributed.
