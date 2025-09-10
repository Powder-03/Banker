import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

class TestBranchEndpoints:
    """Test branch-related API endpoints"""
    
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self, sample_banks, sample_branches):
        """Setup test data"""
        self.banks = sample_banks
        self.branches = sample_branches
    
    def test_get_branch_by_ifsc_success(self, client: TestClient):
        """Test GET /api/v1/branches/{ifsc} with valid IFSC"""
        ifsc = "SBIN0000001"
        response = client.get(f"/api/v1/branches/{ifsc}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert data["ifsc"] == ifsc
        assert data["bank_id"] == 1
        assert data["branch"] == "NEW DELHI MAIN BRANCH"
        assert data["city"] == "NEW DELHI"
        assert data["state"] == "DELHI"
        assert "bank_name" in data
    
    def test_get_branch_by_ifsc_not_found(self, client: TestClient):
        """Test GET /api/v1/branches/{ifsc} with invalid IFSC"""
        response = client.get("/api/v1/branches/INVALID123")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Branch not found"
    
    def test_search_branches_no_filters(self, client: TestClient):
        """Test GET /api/v1/branches/ without filters"""
        response = client.get("/api/v1/branches/")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check pagination structure
        assert "items" in data
        assert "total" in data
        assert "skip" in data
        assert "limit" in data
        assert "has_next" in data
        assert "has_prev" in data
        
        # Check items
        assert isinstance(data["items"], list)
        assert data["total"] == 4  # We have 4 sample branches
        assert len(data["items"]) <= data["limit"]
    
    def test_search_branches_by_city(self, client: TestClient):
        """Test GET /api/v1/branches/ with city filter"""
        response = client.get("/api/v1/branches/?city=MUMBAI")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check that all returned branches are from Mumbai
        for branch in data["items"]:
            assert "MUMBAI" in branch["city"].upper()
    
    def test_search_branches_by_state(self, client: TestClient):
        """Test GET /api/v1/branches/ with state filter"""
        response = client.get("/api/v1/branches/?state=DELHI")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check that all returned branches are from Delhi
        for branch in data["items"]:
            assert "DELHI" in branch["state"].upper()
    
    def test_search_branches_by_bank_id(self, client: TestClient):
        """Test GET /api/v1/branches/ with bank_id filter"""
        response = client.get("/api/v1/branches/?bank_id=1")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check that all returned branches belong to bank_id 1
        for branch in data["items"]:
            assert branch["bank_id"] == 1
    
    def test_search_branches_with_query(self, client: TestClient):
        """Test GET /api/v1/branches/ with search query"""
        response = client.get("/api/v1/branches/?q=MAIN")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check that results contain the search term
        for branch in data["items"]:
            branch_text = f"{branch['branch']} {branch['address']}".upper()
            assert "MAIN" in branch_text
    
    def test_search_branches_pagination(self, client: TestClient):
        """Test GET /api/v1/branches/ with pagination"""
        # Test first page
        response = client.get("/api/v1/branches/?limit=2&skip=0")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["items"]) <= 2
        assert data["skip"] == 0
        assert data["limit"] == 2
        assert data["has_prev"] == False
        
        # Test second page if there are more items
        if data["total"] > 2:
            response2 = client.get("/api/v1/branches/?limit=2&skip=2")
            assert response2.status_code == 200
            data2 = response2.json()
            assert data2["skip"] == 2
            assert data2["has_prev"] == True
    
    def test_get_branches_by_bank_id(self, client: TestClient):
        """Test GET /api/v1/branches/bank/{bank_id}"""
        bank_id = 1
        response = client.get(f"/api/v1/branches/bank/{bank_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check pagination structure
        assert "items" in data
        assert "total" in data
        
        # Check that all branches belong to the specified bank
        for branch in data["items"]:
            assert branch["bank_id"] == bank_id
    
    def test_get_branches_by_invalid_bank_id(self, client: TestClient):
        """Test GET /api/v1/branches/bank/{bank_id} with invalid bank ID"""
        response = client.get("/api/v1/branches/bank/999")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    @pytest.mark.parametrize("ifsc,expected_bank_id,expected_city", [
        ("SBIN0000001", 1, "NEW DELHI"),
        ("SBIN0000002", 1, "MUMBAI"),
        ("PUNB0000001", 2, "NEW DELHI"),
        ("HDFC0000001", 3, "MUMBAI"),
    ])
    def test_branches_parametrized(self, client: TestClient, ifsc, expected_bank_id, expected_city):
        """Test GET /api/v1/branches/{ifsc} with different IFSC codes"""
        response = client.get(f"/api/v1/branches/{ifsc}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["ifsc"] == ifsc
        assert data["bank_id"] == expected_bank_id
        assert data["city"] == expected_city
    
    def test_search_branches_multiple_filters(self, client: TestClient):
        """Test GET /api/v1/branches/ with multiple filters"""
        response = client.get("/api/v1/branches/?city=MUMBAI&bank_id=1")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check that results match all filters
        for branch in data["items"]:
            assert "MUMBAI" in branch["city"].upper()
            assert branch["bank_id"] == 1
