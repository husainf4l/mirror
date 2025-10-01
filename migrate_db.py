#!/usr/bin/env python3
"""
Database migration script for the wedding mirror application.
Creates the database schema with all required tables.
"""

import sys
from sqlalchemy import create_engine, text
from database import Base
from models import Guest
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_database_schema():
    """Create all database tables"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL not found in environment variables")
        return False
    
    print(f"Connecting to database: {database_url}")
    
    try:
        # Create sync engine for migration
        engine = create_engine(database_url, echo=True)
        
        # Create schema first
        with engine.connect() as conn:
            print("Creating mirror_app schema...")
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS mirror_app"))
            conn.commit()
        
        # Create all tables
        print("Creating database tables...")
        Base.metadata.create_all(engine)
        print("✅ Database schema created successfully!")
        
        engine.dispose()
        return True
        
    except Exception as e:
        print(f"❌ Error creating database schema: {e}")
        return False

def main():
    """Main migration function"""
    print("🚀 Starting database migration...")
    
    success = create_database_schema()
    
    if success:
        print("✅ Database migration completed successfully!")
        sys.exit(0)
    else:
        print("❌ Database migration failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
