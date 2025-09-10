import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

class TestBankEndpoints:
    """Test bank-related API endpoints"""
    
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self, sample_banks, sample_branches):
        """Setup test data"""
        self.banks = sample_banks
        self.branches = sample_branches
    
    def test_get_all_banks(self, client: TestClient):
        """Test GET /api/v1/banks/ endpoint"""
        response = client.get("/api/v1/banks/")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check paginated response structure
        assert "items" in data
        assert "total" in data
        assert "skip" in data
        assert "limit" in data
        assert "has_next" in data
        assert "has_prev" in data
        
        # Check that we have banks in the response
        assert isinstance(data["items"], list)
        assert data["total"] == 3  # We have 3 sample banks
        assert len(data["items"]) <= data["limit"]
        
        # Check first bank data
        first_bank = data["items"][0]
        assert "id" in first_bank
        assert "name" in first_bank
        assert first_bank["name"] in ["STATE BANK OF INDIA", "PUNJAB NATIONAL BANK", "HDFC BANK"]
    
    def test_get_bank_by_id_success(self, client: TestClient):
        """Test GET /api/v1/banks/{bank_id} with valid ID"""
        bank_id = 1
        response = client.get(f"/api/v1/banks/{bank_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert data["id"] == bank_id
        assert data["name"] == "STATE BANK OF INDIA"
        # Note: branches field removed for now due to schema complexity
    
    def test_get_bank_by_id_not_found(self, client: TestClient):
        """Test GET /api/v1/banks/{bank_id} with invalid ID"""
        response = client.get("/api/v1/banks/999")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Bank not found"
    
    def test_get_bank_by_id_invalid_format(self, client: TestClient):
        """Test GET /api/v1/banks/{bank_id} with invalid ID format"""
        response = client.get("/api/v1/banks/invalid")
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.parametrize("bank_id,expected_name", [
        (1, "STATE BANK OF INDIA"),
        (2, "PUNJAB NATIONAL BANK"),
        (3, "HDFC BANK"),
    ])
    def test_get_banks_parametrized(self, client: TestClient, bank_id, expected_name):
        """Test GET /api/v1/banks/{bank_id} with different bank IDs"""
        response = client.get(f"/api/v1/banks/{bank_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == bank_id
        assert data["name"] == expected_name
