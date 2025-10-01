#!/usr/bin/env python3
"""
Schema update script to:
1. Rename seat_number to table_number
2. Make relation nullable
"""

import sys
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def update_schema():
    """Update the database schema"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL not found in environment variables")
        return False
    
    # Convert async URL to sync URL for migration
    if database_url.startswith("postgresql+asyncpg:"):
        database_url = database_url.replace("postgresql+asyncpg:", "postgresql:")
    
    print(f"Connecting to database: {database_url}")
    
    try:
        # Create sync engine
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            print("🔄 Updating database schema...")
            
            # 1. Rename seat_number to table_number
            print("Renaming seat_number column to table_number...")
            conn.execute(text("""
                ALTER TABLE mirror_app.guests 
                RENAME COLUMN seat_number TO table_number
            """))
            
            # 2. Make relation nullable
            print("Making relation column nullable...")
            conn.execute(text("""
                ALTER TABLE mirror_app.guests 
                ALTER COLUMN relation DROP NOT NULL
            """))
            
            conn.commit()
        
        engine.dispose()
        print("✅ Schema update completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error updating schema: {e}")
        return False

def main():
    """Main function"""
    print("🔧 Updating database schema...")
    
    success = update_schema()
    
    if success:
        print("✅ Schema update completed successfully!")
        print("📝 Changes applied:")
        print("   • Renamed seat_number to table_number")
        print("   • Made relation column optional (nullable)")
        sys.exit(0)
    else:
        print("❌ Schema update failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
