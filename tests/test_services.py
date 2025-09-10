import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.bank_service import BankService
from app.services.branch_service import BranchService
from app.models.bank import Bank
from app.models.branch import Branch

class TestBankService:
    """Test bank service layer"""
    
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self, sample_banks, sample_branches):
        """Setup test data"""
        self.banks = sample_banks
        self.branches = sample_branches
    
    async def test_get_all_banks(self, test_db: AsyncSession):
        """Test BankService.get_all_banks()"""
        banks = await BankService.get_all_banks(test_db)
        
        assert len(banks) == 3
        # Check that results include bank and branch count
        for bank_row in banks:
            bank = bank_row[0]  # Bank object
            branch_count = bank_row[1]  # Branch count
            assert isinstance(bank, Bank)
            assert isinstance(branch_count, int)
            assert branch_count >= 0
    
    async def test_get_bank_by_id_exists(self, test_db: AsyncSession):
        """Test BankService.get_bank_by_id() with existing bank"""
        bank = await BankService.get_bank_by_id(test_db, 1)
        
        assert bank is not None
        assert bank.id == 1
        assert bank.name == "STATE BANK OF INDIA"
        assert hasattr(bank, 'branches')
    
    async def test_get_bank_by_id_not_exists(self, test_db: AsyncSession):
        """Test BankService.get_bank_by_id() with non-existing bank"""
        bank = await BankService.get_bank_by_id(test_db, 999)
        
        assert bank is None
    
    async def test_get_bank_count(self, test_db: AsyncSession):
        """Test BankService.get_bank_count()"""
        count = await BankService.get_bank_count(test_db)
        
        assert count == 3

class TestBranchService:
    """Test branch service layer"""
    
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self, sample_banks, sample_branches):
        """Setup test data"""
        self.banks = sample_banks
        self.branches = sample_branches
    
    async def test_get_branch_by_ifsc_exists(self, test_db: AsyncSession):
        """Test BranchService.get_branch_by_ifsc() with existing IFSC"""
        branch = await BranchService.get_branch_by_ifsc(test_db, "SBIN0000001")
        
        assert branch is not None
        assert branch.ifsc == "SBIN0000001"
        assert branch.bank_id == 1
        assert hasattr(branch, 'bank_name')
    
    async def test_get_branch_by_ifsc_not_exists(self, test_db: AsyncSession):
        """Test BranchService.get_branch_by_ifsc() with non-existing IFSC"""
        branch = await BranchService.get_branch_by_ifsc(test_db, "INVALID123")
        
        assert branch is None
    
    async def test_search_branches_no_filters(self, test_db: AsyncSession):
        """Test BranchService.search_branches() without filters"""
        branches, total = await BranchService.search_branches(test_db)
        
        assert len(branches) == 4  # All sample branches
        assert total == 4
        
        # Check that bank_name is populated
        for branch in branches:
            assert hasattr(branch, 'bank_name')
            assert branch.bank_name is not None
    
    async def test_search_branches_by_city(self, test_db: AsyncSession):
        """Test BranchService.search_branches() with city filter"""
        branches, total = await BranchService.search_branches(test_db, city="MUMBAI")
        
        assert total == 2  # Two Mumbai branches
        for branch in branches:
            assert "MUMBAI" in branch.city.upper()
    
    async def test_search_branches_by_state(self, test_db: AsyncSession):
        """Test BranchService.search_branches() with state filter"""
        branches, total = await BranchService.search_branches(test_db, state="DELHI")
        
        assert total == 2  # Two Delhi branches
        for branch in branches:
            assert "DELHI" in branch.state.upper()
    
    async def test_search_branches_by_bank_id(self, test_db: AsyncSession):
        """Test BranchService.search_branches() with bank_id filter"""
        branches, total = await BranchService.search_branches(test_db, bank_id=1)
        
        assert total == 2  # Two SBI branches
        for branch in branches:
            assert branch.bank_id == 1
    
    async def test_search_branches_with_query(self, test_db: AsyncSession):
        """Test BranchService.search_branches() with search query"""
        branches, total = await BranchService.search_branches(test_db, query="MAIN")
        
        assert total >= 1  # At least one main branch
        for branch in branches:
            branch_text = f"{branch.branch} {branch.address}".upper()
            assert "MAIN" in branch_text
    
    async def test_search_branches_pagination(self, test_db: AsyncSession):
        """Test BranchService.search_branches() with pagination"""
        # First page
        branches_page1, total = await BranchService.search_branches(
            test_db, skip=0, limit=2
        )
        
        assert len(branches_page1) == 2
        assert total == 4
        
        # Second page
        branches_page2, total2 = await BranchService.search_branches(
            test_db, skip=2, limit=2
        )
        
        assert len(branches_page2) == 2
        assert total2 == 4
        
        # Check that pages contain different branches
        page1_ifsc = {branch.ifsc for branch in branches_page1}
        page2_ifsc = {branch.ifsc for branch in branches_page2}
        assert page1_ifsc.isdisjoint(page2_ifsc)
    
    async def test_get_branches_by_bank_id(self, test_db: AsyncSession):
        """Test BranchService.get_branches_by_bank_id()"""
        branches, total = await BranchService.get_branches_by_bank_id(test_db, 1)
        
        assert total == 2  # Two SBI branches
        assert len(branches) == 2
        
        for branch in branches:
            assert branch.bank_id == 1
            assert hasattr(branch, 'bank_name')
    
    async def test_get_branch_count(self, test_db: AsyncSession):
        """Test BranchService.get_branch_count()"""
        count = await BranchService.get_branch_count(test_db)
        
        assert count == 4

class TestServiceIntegration:
    """Test integration between services"""
    
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self, sample_banks, sample_branches):
        """Setup test data"""
        self.banks = sample_banks
        self.branches = sample_branches
    
    async def test_bank_branch_relationship(self, test_db: AsyncSession):
        """Test that bank-branch relationships work correctly"""
        # Get bank with branches
        bank = await BankService.get_bank_by_id(test_db, 1)
        assert bank is not None
        
        # Get branches for the same bank
        branches, total = await BranchService.get_branches_by_bank_id(test_db, 1)
        
        # Check consistency
        assert len(bank.branches) == total
        assert len(bank.branches) == len(branches)
    
    async def test_data_consistency(self, test_db: AsyncSession):
        """Test data consistency across services"""
        # Get all banks
        banks = await BankService.get_all_banks(test_db)
        bank_count = await BankService.get_bank_count(test_db)
        
        assert len(banks) == bank_count
        
        # Get all branches
        branches, total_branches = await BranchService.search_branches(test_db, limit=1000)
        branch_count = await BranchService.get_branch_count(test_db)
        
        assert total_branches == branch_count
        assert len(branches) == branch_count
