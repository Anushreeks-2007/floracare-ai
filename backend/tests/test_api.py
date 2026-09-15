import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_root():
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["system"] == "FloraCare AI"

def test_flower_catalog():
    res = client.get("/api/flowers")
    assert res.status_code == 200
    data = res.json()
    assert data["count"] == 102

def test_flower_search():
    res = client.get("/api/flowers?q=orchid")
    assert res.status_code == 200
    data = res.json()
    assert data["count"] >= 2

def test_flower_detail():
    res = client.get("/api/flowers/1")
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == 1
    assert "temperature" in data
    assert "watering" in data

def test_compare_flowers():
    res = client.get("/api/flowers/compare?id1=1&id2=2")
    assert res.status_code == 200
    data = res.json()
    assert "plant1" in data
    assert "plant2" in data
    assert "radar_data" in data["comparison"]

def test_recommender():
    req = {
        "temperature": 24.0,
        "humidity": 65.0,
        "sunlight_hours": 6.0,
        "soil_type": "loamy",
        "soil_ph": 6.5,
        "watering_frequency": "2 times per week"
    }
    res = client.post("/api/flowers/recommender", json=req)
    assert res.status_code == 200
    data = res.json()
    assert len(data["top_recommendations"]) > 0
    assert "reasons" in data["top_recommendations"][0]

def test_health_score():
    req = {
        "flower_id": 1,
        "temperature": 15.0,
        "humidity": 65.0,
        "sunlight_hours": 4.0,
        "soil_ph": 6.5,
        "soil_type": "loamy",
        "watering_frequency": "2-3 times per week"
    }
    res = client.post("/api/care/health-score", json=req)
    assert res.status_code == 200
    data = res.json()
    assert 0 <= data["score"] <= 100
    assert "grade" in data

def test_action_plan():
    req = {
        "flower_id": 1,
        "temperature": 15.0,
        "humidity": 65.0,
        "sunlight_hours": 4.0
    }
    res = client.post("/api/care/action-plan", json=req)
    assert res.status_code == 200
    data = res.json()
    assert len(data["tasks"]) >= 3

def test_watering_advisor():
    req = {
        "flower_id": 1,
        "temperature": 15.0,
        "humidity": 65.0,
        "soil_type": "loamy"
    }
    res = client.post("/api/care/watering-advisor", json=req)
    assert res.status_code == 200
    data = res.json()
    assert "recommendation" in data
    assert "reason" in data

def test_what_if_simulator():
    req = {
        "flower_id": 1,
        "base_env": {"temperature": 12.0, "humidity": 50.0},
        "modifications": {"temperature": 16.0, "humidity": 65.0}
    }
    res = client.post("/api/care/what-if", json=req)
    assert res.status_code == 200
    data = res.json()
    assert "original_score" in data
    assert "new_score" in data

def test_analytics_endpoints():
    r1 = client.get("/api/analytics/summary")
    assert r1.status_code == 200
    r2 = client.get("/api/analytics/mining")
    assert r2.status_code == 200

def test_profiles_crud():
    # Create profile
    p_req = {"flower_id": 1, "nickname": "Test Rose", "location": "Balcony"}
    r = client.post("/api/profiles", json=p_req)
    assert r.status_code == 200
    p = r.json()
    p_id = p["id"]

    # List profiles
    r_list = client.get("/api/profiles")
    assert any(x["id"] == p_id for x in r_list.json())

    # Delete profile
    r_del = client.delete(f"/api/profiles/{p_id}")
    assert r_del.status_code == 200
