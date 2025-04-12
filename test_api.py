import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api"
CURRENT_USER = "AkarshanGupta"
CURRENT_TIME = "2025-04-10 12:41:56"

def print_json(data, title):
    print("\n" + "=" * 50)
    print(f"{title}:")
    print("=" * 50)
    print(json.dumps(data, indent=2))
    print("\n")

def test_api():
    # 1. System Information
    print("Testing System Information...")
    response = requests.get(f"{BASE_URL}/system-info")
    print_json(response.json(), "System Info")

    # 2. Check Initial Inventory for all stores
    stores = ["store1", "store2", "store3"]
    for store in stores:
        print(f"Checking inventory for {store}...")
        response = requests.get(f"{BASE_URL}/inventory/{store}")
        print_json(response.json(), f"{store} Inventory")

    # 3. Update Inventory (Add more T-shirts to store1)
    update_data = {
        "product_id": "P001",  # T-Shirt
        "quantity": 30,
        "store_id": "store1"
    }
    print("Updating inventory...")
    response = requests.post(f"{BASE_URL}/inventory/update", json=update_data)
    print_json(response.json(), "Inventory Update Result")

    # 4. Get Forecast for store1
    print("Getting forecast for store1...")
    response = requests.get(f"{BASE_URL}/forecast/store1")
    print_json(response.json(), "Store1 Forecast")

    # 5. Get Optimization Recommendations
    print("Getting optimization recommendations...")
    response = requests.get(f"{BASE_URL}/optimize/store1")
    print_json(response.json(), "Optimization Recommendations")

if __name__ == "__main__":
    print(f"Starting API tests at {CURRENT_TIME}")
    print(f"Current user: {CURRENT_USER}")
    try:
        test_api()
        print("\nAll tests completed successfully!")
    except Exception as e:
        print(f"Error during testing: {str(e)}")