import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
import sys

# Set TESTING environment variable before importing any other modules
os.environ["TESTING"] = "1"

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Create test database
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Import after setting up test database
from database.database import Base, Ship, get_db
from main import app

# Override the get_db dependency to use our test database
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create test client
client = TestClient(app)

# Test data
test_ship = {
    "name": "Test Ship",
    "year_built": 1990,
    "commissioned_date": 1991,
    "stricken_date": 2020,
    "country_of_origin": "USA"
}

@pytest.fixture(autouse=True)
def setup_database():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create test session
    db = TestingSessionLocal()
    
    # Add test data
    test_ship_db = Ship(**test_ship)
    db.add(test_ship_db)
    db.commit()
    
    yield
    
    # Clean up after tests
    Base.metadata.drop_all(bind=engine)

def test_get_ships():
    response = client.get("/ships/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["name"] == test_ship["name"]

def test_add_ship():
    new_ship = {
        "name": "New Ship",
        "year_built": 2000,
        "commissioned_date": 2001,
        "stricken_date": None,
        "country_of_origin": "UK"
    }
    
    response = client.post("/ships/", json=new_ship)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == new_ship["name"]
    assert data["year_built"] == new_ship["year_built"]
    assert "id" in data

def test_search_ships():
    # Test search by name
    response = client.get("/ships/search/?query=Test")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["name"] == test_ship["name"]
    
    # Test search by country
    response = client.get("/ships/search/?query=USA")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["country_of_origin"] == "USA"

def test_filter_ships():
    # Test filter by year range
    response = client.get("/ships/filter/?year_from=1980&year_to=2000")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["year_built"] == test_ship["year_built"]
    
    # Test filter by country
    response = client.get("/ships/filter/?country=USA")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["country_of_origin"] == "USA"
    
    # Test filter by commissioned date
    response = client.get("/ships/filter/?commissioned_from=1990&commissioned_to=1992")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["commissioned_date"] == test_ship["commissioned_date"]

def test_update_ship():
    # First, get the ship ID
    response = client.get("/ships/")
    ship_id = response.json()[0]["id"]
    
    # Update the ship
    updated_data = {
        "name": "Updated Ship",
        "year_built": 1995,
        "commissioned_date": 1996,
        "stricken_date": 2021,
        "country_of_origin": "UK"
    }
    
    response = client.put(f"/ships/{ship_id}", json=updated_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == updated_data["name"]
    assert data["year_built"] == updated_data["year_built"]
    assert data["country_of_origin"] == updated_data["country_of_origin"]

def test_delete_ship():
    # First, get the ship ID
    response = client.get("/ships/")
    ship_id = response.json()[0]["id"]
    
    # Delete the ship
    response = client.delete(f"/ships/{ship_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Ship deleted successfully"
    
    # Verify ship is deleted
    response = client.get("/ships/")
    data = response.json()
    assert len(data) == 0

def test_sort_ships():
    # Test sorting by year_built ascending
    response = client.get("/ships/sort/?field=year_built&ascending=true")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    
    # Test sorting by name descending
    response = client.get("/ships/sort/?field=name&ascending=false")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    
    # Test invalid sort field
    response = client.get("/ships/sort/?field=invalid_field")
    assert response.status_code == 400
    assert "Invalid sort field" in response.json()["detail"]

def test_sort_by_service_duration():
    # Add additional test ships with different service durations
    additional_ships = [
        {
            "name": "Short Service Ship",
            "year_built": 2000,
            "commissioned_date": 2001,
            "stricken_date": 2005,
            "country_of_origin": "UK"
        },
        {
            "name": "Long Service Ship",
            "year_built": 1990,
            "commissioned_date": 1991,
            "stricken_date": 2020,
            "country_of_origin": "USA"
        }
    ]
    
    # Add the ships to the database
    for ship_data in additional_ships:
        response = client.post("/ships/", json=ship_data)
        assert response.status_code == 200
    
    # Test ascending sort (shortest service first)
    response = client.get("/ships/sort/service-duration/?ascending=true")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3  # Including the default test ship
    assert data[0]["name"] == "Short Service Ship"  # 4 years service
    assert data[1]["name"] == "Test Ship"          # 29 years service
    assert data[2]["name"] == "Long Service Ship"  # 29 years service
    
    # Test descending sort (longest service first)
    response = client.get("/ships/sort/service-duration/?ascending=false")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3  # Including the default test ship
    assert data[0]["name"] in ["Test Ship", "Long Service Ship"]  # Both have 29 years service
    assert data[1]["name"] in ["Test Ship", "Long Service Ship"]  # Both have 29 years service
    assert data[2]["name"] == "Short Service Ship"  # 4 years service

def test_error_handling():
    # Test updating non-existent ship
    response = client.put("/ships/999", json=test_ship)
    assert response.status_code == 404
    assert response.json()["detail"] == "Ship not found"
    
    # Test deleting non-existent ship
    response = client.delete("/ships/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Ship not found"
    
    # Test invalid ship data
    invalid_ship = {
        "name": "",  # Empty name
        "year_built": "invalid",  # Invalid year
        "commissioned_date": "invalid",  # Invalid date
        "stricken_date": "invalid",  # Invalid date
        "country_of_origin": None
    }
    
    response = client.post("/ships/", json=invalid_ship)
    assert response.status_code == 422  # Validation error 