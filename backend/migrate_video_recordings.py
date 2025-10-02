"""
Add video recordings table

This migration adds the video_recordings table to store video links and metadata
from the wedding mirror recording sessions.
"""

from sqlalchemy import create_engine, text
import os
from datetime import datetime

def upgrade():
    """Add video_recordings table"""
    
    # Get database URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable not set")
    
    # Convert async URL to sync URL for migration
    sync_database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
    
    engine = create_engine(sync_database_url)
    
    # Create video_recordings table
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS video_recordings (
        id SERIAL PRIMARY KEY,
        room_id VARCHAR(100) NOT NULL,
        video_url TEXT NOT NULL,
        presigned_url TEXT,
        egress_id VARCHAR(100),
        
        -- Guest information
        guest_id INTEGER REFERENCES guests(id),
        guest_name VARCHAR(200),
        guest_phone VARCHAR(20),
        guest_relation VARCHAR(100),
        guest_table VARCHAR(10),
        
        -- Recording metadata
        recording_started_at TIMESTAMP,
        recording_ended_at TIMESTAMP,
        duration_seconds INTEGER,
        file_size_bytes INTEGER,
        
        -- Status and processing
        is_processed BOOLEAN DEFAULT FALSE NOT NULL,
        is_available BOOLEAN DEFAULT TRUE NOT NULL,
        processing_status VARCHAR(50) DEFAULT 'pending' NOT NULL,
        error_message TEXT,
        
        -- Timestamps
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
    );
    """
    
    # Create indexes for performance
    create_indexes_sql = [
        "CREATE INDEX IF NOT EXISTS idx_video_recordings_room_id ON video_recordings(room_id);",
        "CREATE INDEX IF NOT EXISTS idx_video_recordings_guest_id ON video_recordings(guest_id);",
        "CREATE INDEX IF NOT EXISTS idx_video_recordings_guest_name ON video_recordings(guest_name);",
        "CREATE INDEX IF NOT EXISTS idx_video_recordings_egress_id ON video_recordings(egress_id);",
        "CREATE INDEX IF NOT EXISTS idx_video_recordings_created_at ON video_recordings(created_at);",
        "CREATE INDEX IF NOT EXISTS idx_video_recordings_status ON video_recordings(processing_status, is_available);"
    ]
    
    # Create trigger for updated_at
    trigger_sql = """
    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = CURRENT_TIMESTAMP;
        RETURN NEW;
    END;
    $$ language 'plpgsql';

    DROP TRIGGER IF EXISTS update_video_recordings_updated_at ON video_recordings;
    CREATE TRIGGER update_video_recordings_updated_at
        BEFORE UPDATE ON video_recordings
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    """
    
    with engine.connect() as connection:
        # Start transaction
        trans = connection.begin()
        
        try:
            # Create table
            print("Creating video_recordings table...")
            connection.execute(text(create_table_sql))
            
            # Create indexes
            print("Creating indexes...")
            for index_sql in create_indexes_sql:
                connection.execute(text(index_sql))
            
            # Create trigger
            print("Creating updated_at trigger...")
            connection.execute(text(trigger_sql))
            
            # Commit transaction
            trans.commit()
            print("✅ Video recordings table created successfully!")
            
        except Exception as e:
            trans.rollback()
            print(f"❌ Error creating video recordings table: {e}")
            raise


def downgrade():
    """Drop video_recordings table"""
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable not set")
    
    sync_database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
    engine = create_engine(sync_database_url)
    
    drop_sql = """
    DROP TRIGGER IF EXISTS update_video_recordings_updated_at ON video_recordings;
    DROP FUNCTION IF EXISTS update_updated_at_column();
    DROP TABLE IF EXISTS video_recordings;
    """
    
    with engine.connect() as connection:
        trans = connection.begin()
        
        try:
            connection.execute(text(drop_sql))
            trans.commit()
            print("✅ Video recordings table dropped successfully!")
            
        except Exception as e:
            trans.rollback()
            print(f"❌ Error dropping video recordings table: {e}")
            raise


if __name__ == "__main__":
    import sys
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    if len(sys.argv) > 1 and sys.argv[1] == "downgrade":
        downgrade()
    else:
        upgrade()
