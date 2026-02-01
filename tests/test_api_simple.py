"""
Tests für API Endpoints (Vereinfacht)
"""
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """FastAPI Test Client"""
    from api.main import app
    return TestClient(app)


class TestHealthEndpoints:
    """Tests für Health Check Endpoints"""
    
    def test_root_endpoint(self, client):
        """Test: Root Endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "online"


class TestBrokerEndpoints:
    """Tests für Broker Endpoints"""
    
    def test_bot_status(self, client):
        """Test: Bot Status abrufen"""
        response = client.get("/bot/status")
        assert response.status_code == 200
        data = response.json()
        assert "connected" in data


class TestStopLossEndpoints:
    """Tests für Stop-Loss Endpoints"""
    
    def test_set_stop_loss_without_broker(self, client):
        """Test: Stop-Loss ohne Broker Connection"""
        response = client.post("/stop-loss/set", json={
            "symbol": "AAPL",
            "stop_type": "fixed",
            "stop_price": 145.0
        })
        assert response.status_code == 400
        detail = response.json()["detail"].lower()
        assert "nicht verbunden" in detail or "not connected" in detail
