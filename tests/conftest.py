import pytest
import pytest_asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import get_db, Base
from app.models.bank import Bank
from app.models.branch import Branch

# Test database URL - use in-memory SQLite for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False}
)

# Create test session factory
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

@pytest_asyncio.fixture
async def test_db():
    """Create test database and tables"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestSessionLocal() as session:
        yield session
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def client(test_db):
    """Create test client with test database"""
    async def override_get_db():
        async with TestSessionLocal() as session:
            yield session
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Use TestClient for testing instead of AsyncClient
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def sample_banks(test_db):
    """Create sample banks for testing"""
    banks_data = [
        {"id": 1, "name": "STATE BANK OF INDIA"},
        {"id": 2, "name": "PUNJAB NATIONAL BANK"},
        {"id": 3, "name": "HDFC BANK"},
    ]
    
    banks = []
    for bank_data in banks_data:
        bank = Bank(**bank_data)
        test_db.add(bank)
        banks.append(bank)
    
    await test_db.commit()
    return banks

@pytest_asyncio.fixture
async def sample_branches(test_db, sample_banks):
    """Create sample branches for testing"""
    branches_data = [
        {
            "ifsc": "SBIN0000001",
            "bank_id": 1,
            "branch": "NEW DELHI MAIN BRANCH",
            "address": "11, SANSAD MARG, NEW DELHI",
            "city": "NEW DELHI",
            "district": "NEW DELHI",
            "state": "DELHI"
        },
        {
            "ifsc": "SBIN0000002",
            "bank_id": 1,
            "branch": "MUMBAI MAIN BRANCH",
            "address": "MUMBAI SAMACHAR MARG, MUMBAI",
            "city": "MUMBAI",
            "district": "GREATER MUMBAI",
            "state": "MAHARASHTRA"
        },
        {
            "ifsc": "PUNB0000001",
            "bank_id": 2,
            "branch": "DELHI MAIN BRANCH",
            "address": "7, BHIKAJI CAMA PLACE, NEW DELHI",
            "city": "NEW DELHI",
            "district": "NEW DELHI",
            "state": "DELHI"
        },
        {
            "ifsc": "HDFC0000001",
            "bank_id": 3,
            "branch": "MUMBAI MAIN BRANCH",
            "address": "HDFC BANK HOUSE, MUMBAI",
            "city": "MUMBAI",
            "district": "GREATER MUMBAI",
            "state": "MAHARASHTRA"
        },
    ]
    
    branches = []
    for branch_data in branches_data:
        branch = Branch(**branch_data)
        test_db.add(branch)
        branches.append(branch)
    
    await test_db.commit()
    return branches
