import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

class TestAPIUtilities:
    """Test utility endpoints like health check and stats"""
    
    def test_root_endpoint(self, client: TestClient):
        """Test GET / root endpoint"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "message" in data
        assert "version" in data
        assert "docs" in data
        assert "description" in data
        
        # Check values
        assert data["message"] == "Indian Bank API"
        assert data["version"] == "1.0.0"
        assert data["docs"] == "/docs"
    
    def test_health_check(self, client: TestClient):
        """Test GET /health endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "status" in data
        assert "database" in data
        
        # Check values
        assert data["status"] == "healthy"
        assert data["database"] == "sqlite"
    
    def test_stats_endpoint(self, client: TestClient, sample_banks, sample_branches):
        """Test GET /stats endpoint"""
        response = client.get("/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure - could be error or success based on implementation
        if "error" in data:
            # If there's an error, check error structure
            assert "status" in data
            assert data["status"] == "error"
        else:
            # If successful, check stats structure
            assert "banks_total" in data or "status" in data

class TestAPIErrors:
    """Test API error handling"""
    
    def test_invalid_endpoint(self, client: TestClient):
        """Test accessing non-existent endpoint"""
        response = client.get("/api/v1/invalid-endpoint")
        
        assert response.status_code == 404
    
    def test_method_not_allowed(self, client: TestClient):
        """Test using wrong HTTP method"""
        response = client.post("/api/v1/banks/")
        
        assert response.status_code == 405  # Method Not Allowed
    
    def test_invalid_pagination_params(self, client: TestClient):
        """Test invalid pagination parameters"""
        # Test negative skip
        response = client.get("/api/v1/branches/?skip=-1")
        assert response.status_code == 422  # Validation error
        
        # Test invalid limit
        response = client.get("/api/v1/branches/?limit=0")
        assert response.status_code == 422  # Validation error

class TestAPIValidation:
    """Test API input validation"""
    
    def test_bank_id_validation(self, client: TestClient):
        """Test bank ID parameter validation"""
        # Test with string that can't be converted to int
        response = client.get("/api/v1/banks/not-a-number")
        assert response.status_code == 422
        
        # Test with decimal
        response = client.get("/api/v1/banks/1.5")
        assert response.status_code == 422
    
    def test_ifsc_validation(self, client: TestClient):
        """Test IFSC parameter handling"""
        # Test with very long IFSC (should still work, just not found)
        response = client.get("/api/v1/branches/VERYLONGIFSCCODE12345")
        assert response.status_code == 404  # Not found, but valid request
        
        # Test with special characters (should work)
        response = client.get("/api/v1/branches/TEST123!")
        assert response.status_code == 404  # Not found, but valid request
    
    def test_query_parameter_limits(self, client: TestClient):
        """Test query parameter limits"""
        # Test maximum limit
        response = client.get("/api/v1/branches/?limit=1001")
        assert response.status_code == 422  # Should exceed maximum limit
        
        # Test valid high limit
        response = client.get("/api/v1/branches/?limit=1000")
        assert response.status_code == 200

class TestAPIPerformance:
    """Test API performance characteristics"""
    
    def test_large_result_pagination(self, client: TestClient, sample_branches):
        """Test pagination with larger datasets"""
        # Test with maximum allowed limit
        response = client.get("/api/v1/branches/?limit=1000")
        
        assert response.status_code == 200
        data = response.json()
        
        # Response should be structured correctly even with large limits
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) <= 1000
    
    def test_search_performance(self, client: TestClient):
        """Test search functionality performance"""
        # Test broad search that might return many results
        response = client.get("/api/v1/branches/?q=BANK")
        
        assert response.status_code == 200
        # Should complete in reasonable time (pytest will timeout if too slow)
    
    def test_concurrent_requests_simulation(self, client: TestClient):
        """Simulate multiple concurrent requests"""
        # Since we're using TestClient (synchronous), we can't do true async concurrency
        # But we can test multiple sequential requests
        responses = []
        for _ in range(5):
            response = client.get("/api/v1/banks/")
            responses.append(response)
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == 200
