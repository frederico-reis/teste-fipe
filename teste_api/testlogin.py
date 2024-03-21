import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_register_user():
    response = client.post("/register", json={"user_id": "test@example.com", "password": "Test@1234"})
    assert response.status_code == 200
    assert response.json() == {"message": "Registration complete"}

def test_register_existing_user():
    response = client.post("/register", json={"user_id": "test@example.com", "password": "Test@1234"})
    assert response.status_code == 400
    assert "User already registered" in response.text

def test_register_invalid_email():
    response = client.post("/register", json={"user_id": "invalidemail", "password": "Test@1234"})
    assert response.status_code == 400
    assert "Invalid email format" in response.text

def test_register_invalid_password():
    response = client.post("/register", json={"user_id": "test@example.com", "password": "weak"})
    assert response.status_code == 400
    assert "Invalid password format" in response.text

def test_login_user():
    response = client.post("/login", json={"user_id": "test@example.com", "password": "Test@1234"})
    assert response.status_code == 200
    assert response.json() == {"message": "Login successful"}

def test_login_invalid_credentials():
    response = client.post("/login", json={"user_id": "test@example.com", "password": "incorrect"})
    assert response.status_code == 401
    assert "Incorrect email or password" in response.text

def test_protected_route_without_token():
    response = client.get("/protected")
    assert response.status_code == 401
    assert "Invalid credentials" in response.text

def test_protected_route_with_invalid_token():
    response = client.get("/protected", headers={"Authorization": "Bearer invalidtoken"})
    assert response.status_code == 401
    assert "Invalid token" in response.text

def test_protected_route_with_valid_token():
    # For demonstration purposes, assuming all tokens are valid
    response = client.get("/protected", headers={"Authorization": "Bearer validtoken"})
    assert response.status_code == 200
    assert "You are accessing protected route!" in response.json()["message"]
