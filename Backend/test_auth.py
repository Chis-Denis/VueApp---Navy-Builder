import requests
import json
from datetime import datetime
import time

BASE_URL = "http://localhost:8000"

def print_response(response, title):
    print(f"\n=== {title} ===")
    print(f"Status Code: {response.status_code}")
    try:
        print("Response:", json.dumps(response.json(), indent=2))
    except:
        print("Response:", response.text)
    print("=" * 50)

def simulate_attack_and_detection(admin_token):
    print("\n=== Simulated Attack Scenario ===")
    # 1. Register attacker
    attacker = {
        "username": "attacker_user",
        "email": "attacker@example.com",
        "password": "attack123"
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=attacker)
    print(f"Attacker registration status: {response.status_code}")
    # 2. Login as attacker
    login_data = {"username": "attacker_user", "password": "attack123"}
    response = requests.post(f"{BASE_URL}/auth/token", data=login_data)
    attacker_token = response.json().get("access_token")
    print(f"Attacker login status: {response.status_code}")
    headers = {"Authorization": f"Bearer {attacker_token}"}
    # 3. Rapidly perform CRUD operations
    ship_ids = []
    for i in range(55):  # Exceed threshold (50)
        ship_data = {
            "name": f"Attack Ship {i}",
            "year_built": 2000 + (i % 20),
            "commissioned_date": 2001 + (i % 20),
            "stricken_date": None,
            "country_of_origin": "EvilLand"
        }
        # Create
        response = requests.post(f"{BASE_URL}/ships/", json=ship_data, headers=headers)
        if response.status_code == 200:
            ship_id = response.json()["id"]
            ship_ids.append(ship_id)
        # Update
        if ship_ids:
            update_data = ship_data.copy()
            update_data["name"] = f"Attack Ship Updated {i}"
            requests.put(f"{BASE_URL}/ships/{ship_ids[-1]}", json=update_data, headers=headers)
        # Delete (every 5th)
        if i % 5 == 0 and ship_ids:
            requests.delete(f"{BASE_URL}/ships/{ship_ids[-1]}", headers=headers)
            ship_ids.pop()
    print(f"Performed {55} rapid CRUD operations as attacker.")
    # 4. Wait for monitoring thread to detect (wait a bit more than check_interval)
    print("Waiting for monitoring thread to analyze logs...")
    time.sleep(310)  # 5 minutes + 10 seconds buffer
    # 5. As admin, check monitored users
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.get(f"{BASE_URL}/auth/admin/monitored-users", headers=admin_headers)
    print("\n=== Monitored Users After Attack ===")
    try:
        print(json.dumps(response.json(), indent=2))
    except Exception:
        print(response.text)
    print("=" * 50)

def test_authentication():
    # 1. Register a regular user
    regular_user = {
        "username": "regular_user",
        "email": "regular@example.com",
        "password": "password123"
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=regular_user)
    print_response(response, "Register Regular User")

    # 2. Register an admin user
    admin_user = {
        "username": "admin_user",
        "email": "admin@example.com",
        "password": "admin123"
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=admin_user)
    print_response(response, "Register Admin User")

    # 3. Login as regular user
    login_data = {
        "username": "regular_user",
        "password": "password123"
    }
    response = requests.post(f"{BASE_URL}/auth/token", data=login_data)
    print_response(response, "Login Regular User")
    regular_token = response.json().get("access_token")

    # 4. Login as admin user
    login_data = {
        "username": "admin_user",
        "password": "admin123"
    }
    response = requests.post(f"{BASE_URL}/auth/token", data=login_data)
    print_response(response, "Login Admin User")
    admin_token = response.json().get("access_token")

    # 5. Get user profile (regular user)
    headers = {"Authorization": f"Bearer {regular_token}"}
    response = requests.get(f"{BASE_URL}/auth/users/me", headers=headers)
    print_response(response, "Get Regular User Profile")

    # 6. Try to access monitored users as regular user (should fail)
    response = requests.get(f"{BASE_URL}/auth/admin/monitored-users", headers=headers)
    print_response(response, "Regular User Accessing Monitored Users (Should Fail)")

    # 7. Access monitored users as admin
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.get(f"{BASE_URL}/auth/admin/monitored-users", headers=headers)
    print_response(response, "Admin Accessing Monitored Users")

    # 8. Create some ships to test activity monitoring
    ship_data = {
        "name": "Test Ship",
        "year_built": 2020,
        "commissioned_date": 2021,
        "stricken_date": None,
        "country_of_origin": "Test Country"
    }
    
    # Create multiple ships to trigger monitoring
    for i in range(60):  # This should trigger the monitoring threshold
        ship_data["name"] = f"Test Ship {i}"
        response = requests.post(
            f"{BASE_URL}/ships/",
            json=ship_data,
            headers=headers
        )
        print(f"Created ship {i+1}/60")
    
    # 9. Check monitored users again after activity
    response = requests.get(f"{BASE_URL}/auth/admin/monitored-users", headers=headers)
    print_response(response, "Monitored Users After Activity")
    # Simulate attack scenario
    simulate_attack_and_detection(admin_token)

if __name__ == "__main__":
    print("Starting authentication system test...")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    test_authentication()
    print("\nTest completed!") 