import os
import json
import asyncio

DATA_FOLDER = "data/1stdibs"

def parse_product(data, source_name):
    """
    Given that 1stdibs, Grailed, and Fashionphile data share very similar JSON structures,
    we can use a unified parsing strategy that looks for the core fields cleanly.
    """
    return {
        "external_id": data.get("product_url", ""),
        "name": data.get("model", "Unknown Product"),
        "brand": data.get("brand", "Unknown Brand"),
        "category": data.get("category") or data.get("metadata", {}).get("garment_type", "luxury_item"),
        "price": data.get("price", 0.0),
        "source": source_name
    }

async def fetch_file_async_with_retry(file_path, source_name, max_retries=3):
    """
    Simulates async data fetching over a network with explicit retry logic.
    Instead of hitting a live URL, it 'fetches' the local JSON file.
    If it encounters an error, it will automatically backoff and retry.
    """
    for attempt in range(max_retries):
        try:
            # Simulated network latency (makes it behave like a remote API call)
            await asyncio.sleep(0.01) 
            
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return parse_product(data, source_name)
                
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"Failed to fetch {file_path} after {max_retries} attempts: {e}")
                return None
            else:
                # Basic exponential backoff if a failure occurs
                await asyncio.sleep(0.1 * (attempt + 1)) 

async def load_all_products_async():
    """
    Gathers all product data fetching into concurrent tasks using asyncio!
    """
    tasks = []
    if not os.path.exists(DATA_FOLDER):
        return []

    for file_name in os.listdir(DATA_FOLDER):
        if not file_name.endswith(".json"): 
            continue
            
        file_path = os.path.join(DATA_FOLDER, file_name)
        
        # Dynamically determine the marketplace route based on filename
        source_name = "1stdibs"
        if "grailed" in file_name.lower():
            source_name = "Grailed"
        elif "fashionphile" in file_name.lower():
            source_name = "Fashionphile"
            
        tasks.append(fetch_file_async_with_retry(file_path, source_name))
        
    # Execute all simulated network fetches concurrently 
    results = await asyncio.gather(*tasks)
    
    # Filter out any files that failed their retries
    return [r for r in results if r is not None]
