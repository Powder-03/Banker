import asyncio
import re
import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import from app
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import engine, AsyncSessionLocal
from app.models.bank import Bank
from app.models.branch import Branch
from app.core.database import Base
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataLoader:
    def __init__(self):
        self.sql_file = "indian_bank.sql"
    
    async def create_tables(self):
        """Create all database tables"""
        logger.info("Creating database tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)  # Drop existing tables
            await conn.run_sync(Base.metadata.create_all)  # Create fresh tables
        logger.info("Database tables created successfully")
    
    async def load_banks_from_sql(self):
        """Load banks from SQL file"""
        logger.info(f"Loading banks from {self.sql_file}")
        
        if not os.path.exists(self.sql_file):
            logger.error(f"SQL file not found: {self.sql_file}")
            return
        
        async with AsyncSessionLocal() as db:
            try:
                with open(self.sql_file, 'r', encoding='utf-8') as file:
                    content = file.read()
                    
                    # Extract bank data using regex
                    bank_pattern = r"COPY banks \(name, id\) FROM stdin;(.*?)\\."
                    match = re.search(bank_pattern, content, re.DOTALL)
                    
                    if match:
                        bank_data = match.group(1).strip()
                        banks_added = 0
                        
                        for line in bank_data.split('\n'):
                            line = line.strip()
                            if line and not line.startswith('--'):
                                parts = line.split('\t')
                                if len(parts) >= 2:
                                    name = parts[0].strip()
                                    try:
                                        bank_id = int(parts[1].strip())
                                        
                                        bank = Bank(id=bank_id, name=name)
                                        db.add(bank)
                                        banks_added += 1
                                        
                                    except ValueError:
                                        logger.warning(f"Invalid bank ID in line: {line}")
                        
                        await db.commit()
                        logger.info(f"Successfully added {banks_added} banks to database")
                    else:
                        logger.warning("No bank data found in SQL file")
                        
            except Exception as e:
                logger.error(f"Error loading banks from SQL: {e}")
                await db.rollback()
                raise
    
    async def load_branches_from_sql(self):
        """Load branches from SQL file"""
        logger.info(f"Loading branches from {self.sql_file}")
        
        if not os.path.exists(self.sql_file):
            logger.error(f"SQL file not found: {self.sql_file}")
            return
        
        async with AsyncSessionLocal() as db:
            try:
                with open(self.sql_file, 'r', encoding='utf-8') as file:
                    content = file.read()
                    
                    # Extract branch data using regex
                    branch_pattern = r"COPY branches \(ifsc, bank_id, branch, address, city, district, state\) FROM stdin;(.*?)\\."
                    match = re.search(branch_pattern, content, re.DOTALL)
                    
                    if match:
                        branch_data = match.group(1).strip()
                        branches_added = 0
                        branches_skipped = 0
                        
                        for line in branch_data.split('\n'):
                            line = line.strip()
                            if line and not line.startswith('--'):
                                parts = line.split('\t')
                                if len(parts) >= 7:
                                    try:
                                        ifsc = parts[0].strip()
                                        bank_id = int(parts[1].strip()) if parts[1].strip() else None
                                        branch_name = parts[2].strip() if parts[2] else None
                                        address = parts[3].strip() if parts[3] else None
                                        city = parts[4].strip() if parts[4] else None
                                        district = parts[5].strip() if parts[5] else None
                                        state = parts[6].strip() if parts[6] else None
                                        
                                        if ifsc and bank_id:
                                            # Verify bank exists
                                            bank_result = await db.execute(select(Bank).where(Bank.id == bank_id))
                                            bank_exists = bank_result.scalar_one_or_none()
                                            
                                            if bank_exists:
                                                branch = Branch(
                                                    ifsc=ifsc.upper(),
                                                    bank_id=bank_id,
                                                    branch=branch_name,
                                                    address=address,
                                                    city=city,
                                                    district=district,
                                                    state=state
                                                )
                                                db.add(branch)
                                                branches_added += 1
                                                
                                                # Commit in batches of 1000
                                                if branches_added % 1000 == 0:
                                                    await db.commit()
                                                    logger.info(f"Committed {branches_added} branches...")
                                            else:
                                                logger.warning(f"Bank ID {bank_id} not found for branch {ifsc}")
                                                branches_skipped += 1
                                        else:
                                            branches_skipped += 1
                                            
                                    except (ValueError, IndexError) as e:
                                        logger.warning(f"Error processing line: {e}")
                                        branches_skipped += 1
                                else:
                                    branches_skipped += 1
                        
                        # Final commit
                        await db.commit()
                        logger.info(f"Successfully added {branches_added} branches to database")
                        if branches_skipped > 0:
                            logger.info(f"Skipped {branches_skipped} branches due to errors")
                    else:
                        logger.warning("No branch data found in SQL file")
                        
            except Exception as e:
                logger.error(f"Error loading branches from SQL: {e}")
                await db.rollback()
                raise
    
    async def get_stats(self):
        """Get database statistics"""
        async with AsyncSessionLocal() as db:
            # Count banks
            bank_result = await db.execute(select(Bank))
            bank_count = len(bank_result.scalars().all())
            
            # Count branches
            branch_result = await db.execute(select(Branch))
            branch_count = len(branch_result.scalars().all())
            
            # Get unique states
            state_result = await db.execute(select(Branch.state).distinct())
            unique_states = len([s for s in state_result.scalars().all() if s])
            
            # Get unique cities
            city_result = await db.execute(select(Branch.city).distinct())
            unique_cities = len([c for c in city_result.scalars().all() if c])
            
            return {
                "banks_count": bank_count,
                "branches_count": branch_count,
                "unique_states": unique_states,
                "unique_cities": unique_cities
            }
    
    async def load_all_data(self):
        """Load all data from SQL file"""
        logger.info("Starting complete data loading process...")
        
        try:
            # Create tables
            await self.create_tables()
            
            # Load banks
            await self.load_banks_from_sql()
            
            # Load branches
            await self.load_branches_from_sql()
            
            # Get and display statistics
            stats = await self.get_stats()
            logger.info("Data loading completed successfully!")
            logger.info(f"Final statistics: {stats}")
            
            return stats
            
        except Exception as e:
            logger.error(f"Data loading failed: {e}")
            raise

async def main():
    """Main function to run data loading"""
    loader = DataLoader()
    
    print("=" * 60)
    print("Indian Bank Data Loader")
    print("=" * 60)
    
    try:
        stats = await loader.load_all_data()
        
        print("\n" + "=" * 60)
        print("DATA LOADING SUMMARY")
        print("=" * 60)
        print(f"Banks loaded: {stats['banks_count']}")
        print(f"Branches loaded: {stats['branches_count']}")
        print(f"Unique states: {stats['unique_states']}")
        print(f"Unique cities: {stats['unique_cities']}")
        print("=" * 60)
        print("✅ Data loading completed successfully!")
        print("You can now start the API server with: uvicorn app.main:app --reload")
        
    except Exception as e:
        print(f"\n❌ Data loading failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
