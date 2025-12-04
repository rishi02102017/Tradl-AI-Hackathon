"""Integration tests for FastAPI endpoints."""
import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


class TestAPIEndpoints:
    """Tests for API endpoints."""
    
    def test_root_endpoint(self):
        """Test root endpoint returns API info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "endpoints" in data
    
    def test_query_endpoint(self):
        """Test query endpoint."""
        response = client.get("/query?q=HDFC%20Bank%20news")
        assert response.status_code == 200
        data = response.json()
        assert "relevant_articles" in data
        assert "count" in data
        assert isinstance(data["count"], int)
    
    def test_query_endpoint_empty(self):
        """Test query endpoint with empty query."""
        response = client.get("/query?q=")
        # Should handle gracefully
        assert response.status_code in [200, 400]
    
    def test_entities_endpoint(self):
        """Test entities endpoint."""
        response = client.get("/entities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
    
    def test_deduplication_demo_endpoint(self):
        """Test deduplication demo endpoint."""
        response = client.get("/deduplication-demo")
        assert response.status_code == 200
        data = response.json()
        assert "total_articles" in data
        assert "unique_stories" in data
        assert "rbi_rate_hike_example" in data
    
    def test_ingest_endpoint(self):
        """Test ingest endpoint."""
        articles = [
            {
                "title": "Test Article",
                "content": "This is a test article about HDFC Bank.",
                "source": "test"
            }
        ]
        response = client.post("/ingest", json=articles)
        # Should accept the request (may process in background)
        assert response.status_code in [200, 202]
    
    def test_news_endpoint(self):
        """Test get news endpoint."""
        # Try to get a news article (may not exist)
        response = client.get("/news/N1")
        # Should handle gracefully
        assert response.status_code in [200, 404]
    
    def test_stocks_endpoint(self):
        """Test stocks endpoint."""
        response = client.get("/stocks/HDFCBANK/news")
        assert response.status_code == 200
        data = response.json()
        assert "symbol" in data
        assert "articles" in data

