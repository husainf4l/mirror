#!/usr/bin/env python3
"""
Database initialization script for the Wedding Mirror application.
Creates tables and populates with sample data.
"""

import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Load environment variables
load_dotenv()

# Import models
from models import Base, Guest, RelationType

def create_tables():
    """Create all database tables."""
    # Get database URL and convert from async to sync
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL not found in environment variables")
    
    # Convert asyncpg URL to psycopg2 for sync operations
    sync_database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
    
    print(f"Creating tables using: {sync_database_url}")
    
    # Create engine and tables
    engine = create_engine(sync_database_url, echo=True)
    Base.metadata.create_all(bind=engine)
    
    print("✅ Tables created successfully!")
    return engine

def seed_database(engine):
    """Populate database with sample wedding guest data."""
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Create relation types
        relation_types = [
            RelationType(name="Bride's Family", description="Family members of the bride"),
            RelationType(name="Groom's Family", description="Family members of the groom"),
            RelationType(name="Bride's Friends", description="Friends of the bride"),
            RelationType(name="Groom's Friends", description="Friends of the groom"),
            RelationType(name="Mutual Friends", description="Friends of both bride and groom"),
            RelationType(name="Work Colleagues", description="Work colleagues"),
            RelationType(name="Other", description="Other relationships")
        ]
        
        for rel_type in relation_types:
            session.add(rel_type)
        session.commit()
        
        print("✅ Relation types created!")
        
        # Get relation type IDs
        bride_family = session.query(RelationType).filter_by(name="Bride's Family").first()
        groom_family = session.query(RelationType).filter_by(name="Groom's Family").first()
        bride_friends = session.query(RelationType).filter_by(name="Bride's Friends").first()
        groom_friends = session.query(RelationType).filter_by(name="Groom's Friends").first()
        mutual_friends = session.query(RelationType).filter_by(name="Mutual Friends").first()
        
        # Sample guests with Arabic names
        sample_guests = [
            # Bride's family
            Guest(
                first_name="Fatima", 
                last_name="Al-Hussein", 
                phone="+962-555-0101",
                seat_number="A1", 
                relation="Mother of the Bride",
                relation_type_id=bride_family.id,
                message="أنا فخورة بك يا ابنتي الحبيبة",
                story="Fatima has been planning this day since her daughter was little.",
                about="Loves cooking traditional Arabic dishes and reading Quran."
            ),
            Guest(
                first_name="Hussein", 
                last_name="Al-Hussein", 
                phone="+962-555-0102",
                seat_number="A2", 
                relation="Father of the Bride",
                relation_type_id=bride_family.id,
                message="أهلاً وسهلاً في العائلة",
                story="Hussein walked his daughter down the aisle with tears of joy.",
                about="Retired engineer who loves reading history books."
            ),
            Guest(
                first_name="Zeinab", 
                last_name="Al-Hussein", 
                phone="+962-555-0103",
                seat_number="A3", 
                relation="Sister of the Bride",
                relation_type_id=bride_family.id,
                message="أفضل أخت وأفضل زوجة أخ!",
                story="Zeinab and the bride have been best friends since childhood.",
                about="Works as a doctor and has three children."
            ),
            
            # Groom's family  
            Guest(
                first_name="Mohammad", 
                last_name="Al-Ahmad", 
                phone="+962-555-0201",
                seat_number="B1", 
                relation="Father of the Groom",
                relation_type_id=groom_family.id,
                message="لا يمكن أن أكون أكثر سعادة لكما!",
                story="Mohammad taught his son the values of respect and kindness.",
                about="Owns a construction company and loves traditional poetry."
            ),
            Guest(
                first_name="Khadija", 
                last_name="Al-Ahmad", 
                phone="+962-555-0202",
                seat_number="B2", 
                relation="Mother of the Groom",
                relation_type_id=groom_family.id,
                message="أنتما مناسبان لبعضكما البعض تماماً",
                story="Khadija immediately loved the bride when they first met.",
                about="Teacher who volunteers at the local mosque."
            ),
            
            # Friends
            Guest(
                first_name="Aisha", 
                last_name="Al-Zahra", 
                phone="+962-555-0301",
                seat_number="C1", 
                relation="Maid of Honor",
                relation_type_id=bride_friends.id,
                message="صديقتي الغالية تستحق الأفضل!",
                story="Aisha and the bride have been friends since university.",
                about="Marketing manager who loves traveling and photography."
            ),
            Guest(
                first_name="Omar", 
                last_name="Al-Khouri", 
                phone="+962-555-0401",
                seat_number="D1", 
                relation="Best Man",
                relation_type_id=groom_friends.id,
                message="مبروك لأعز أصدقائي!",
                story="Omar was the groom's roommate in college.",
                about="Software engineer who plays oud in his free time."
            ),
            Guest(
                first_name="Layla", 
                last_name="Al-Nouri", 
                phone="+962-555-0501",
                seat_number="E1", 
                relation="College Friend",
                relation_type_id=mutual_friends.id,
                message="سعيدة جداً للاحتفال معكما!",
                story="Layla introduced the happy couple at a university event.",
                about="Teacher who loves calligraphy and hiking."
            ),
            
            # Additional guests with various Arabic names for testing
            Guest(
                first_name="Ahmad", 
                last_name="Al-Rashid", 
                phone="+962-555-0601",
                seat_number="F1", 
                relation="Work Colleague",
                relation_type_id=mutual_friends.id,
                message="أتمنى لكما عمراً مديداً مليئاً بالسعادة",
                about="Engineer who specializes in renewable energy."
            ),
            Guest(
                first_name="Maryam", 
                last_name="Al-Qasemi", 
                phone="+962-555-0701",
                seat_number="G1", 
                relation="Neighbor",
                relation_type_id=mutual_friends.id,
                message="زوجان جميلان ما شاء الله!",
                about="Runs a local bakery specializing in Arabic sweets."
            ),
            Guest(
                first_name="Yusuf", 
                last_name="Al-Mansouri", 
                phone="+962-555-0801",
                seat_number="H1", 
                relation="Family Friend",
                relation_type_id=mutual_friends.id,
                message="أعرفكم منذ الصغر!",
                about="Family doctor and longtime friend of both families."
            ),
            Guest(
                first_name="Salma", 
                last_name="Al-Faisal", 
                phone="+962-555-0901",
                seat_number="I1", 
                relation="Cousin",
                relation_type_id=bride_family.id,
                message="ابنة عمي الغالية، مبروك!",
                about="Artist who specializes in Islamic geometric patterns."
            ),
            Guest(
                first_name="Khalid", 
                last_name="Al-Sabah", 
                phone="+962-555-1001",
                seat_number="J1", 
                relation="University Friend",
                relation_type_id=mutual_friends.id,
                message="أصدقاء الجامعة إلى الأبد",
                about="Businessman who imports traditional Arabic goods."
            )
        ]
        
        # Add all guests
        for guest in sample_guests:
            session.add(guest)
        
        session.commit()
        print(f"✅ Added {len(sample_guests)} sample guests!")
        
        # Verify data
        total_guests = session.query(Guest).count()
        print(f"✅ Total guests in database: {total_guests}")
        
        # Show some sample names for testing
        print("\n📋 Sample guest names for testing the agent:")
        sample_names = session.query(Guest.first_name, Guest.last_name, Guest.relation).limit(5).all()
        for first, last, relation in sample_names:
            print(f"  - {first} {last} ({relation})")
            
    except Exception as e:
        session.rollback()
        print(f"❌ Error seeding database: {e}")
        raise
    finally:
        session.close()

def main():
    """Main function to initialize the database."""
    print("🚀 Initializing Wedding Mirror Database...")
    
    try:
        # Create tables
        engine = create_tables()
        
        # Seed with sample data
        seed_database(engine)
        
        print("\n🎉 Database initialization completed successfully!")
        print("\nYou can now:")
        print("1. Test the guest search API endpoint")
        print("2. Run the LiveKit agent to search for guests")
        print("3. Add more guests through the API")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())