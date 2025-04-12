import requests
import json

BASE_URL = "http://localhost:8000/api"

def print_response(response, title):
    print("\n" + "="*50)
    print(f"{title}:")
    print("="*50)
    print(json.dumps(response.json(), indent=2))

def run_demo():
    # 1. Check system info
    response = requests.get(f"{BASE_URL}/system-info")
    print_response(response, "System Information")

    # 2. Check initial inventory for all stores
    for store_id in ["store1", "store2", "store3"]:
        response = requests.get(f"{BASE_URL}/inventory/{store_id}")
        print_response(response, f"Initial Inventory for {store_id}")

    # 3. Update inventory (add stock)
    update_data = {
        "product_id": "P001",
        "quantity": 50,
        "store_id": "store1"
    }
    response = requests.post(f"{BASE_URL}/inventory/update", json=update_data)
    print_response(response, "Inventory Update Result")

    # 4. Check updated inventory
    response = requests.get(f"{BASE_URL}/inventory/store1")
    print_response(response, "Updated Inventory for store1")

    # 5. Get demand forecast
    response = requests.get(f"{BASE_URL}/forecast/store1")
    print_response(response, "Demand Forecast for store1")

    # 6. Get optimization recommendations
    response = requests.get(f"{BASE_URL}/optimize/store1")
    print_response(response, "Optimization Recommendations")

if __name__ == "__main__":
    run_demo()