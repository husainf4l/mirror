#!/usr/bin/env python3
"""
Database seeding script for the wedding mirror application.
Adds sample guest data for testing and development.
"""

import sys
import random
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Guest, RelationType
import os
from dotenv import load_dotenv

# Load environment variables
# Load environment variables from parent directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Sample data for generating realistic guest records with Arabic names
FIRST_NAMES = [
    "Hussein", "Abdullah", "Ibrahim", "Diab", "Mohammed", "Ahmad", "Ali", "Omar", "Khalid", "Yusuf",
    "Hassan", "Mustafa", "Mahmoud", "Hamza", "Tariq", "Saleh", "Karim", "Waleed", "Faisal", "Zaid",
    "Rami", "Nabil", "Samir", "Jamal", "Adnan", "Marwan", "Rashid", "Majid", "Sami", "Ammar",
    "Fatima", "Aisha", "Maryam", "Zainab", "Layla", "Noor", "Hala", "Sarah", "Amina", "Yasmin",
    "Rania", "Dina", "Lina", "Huda", "Rana", "Hanan", "Sana", "Maha", "Salma", "Jana"
]

LAST_NAMES = [
    "Al-Hussein", "Al-Abdullah", "Al-Ibrahim", "Diab", "Al-Mohammed", "Al-Ahmad", "Al-Ali", "Al-Omar", "Al-Khalid", "Al-Hassan",
    "Al-Mustafa", "Al-Mahmoud", "Al-Hamza", "Al-Tariq", "Al-Saleh", "Al-Karim", "Al-Waleed", "Al-Faisal", "Al-Zaid", "Al-Rami",
    "Al-Nabil", "Al-Samir", "Al-Jamal", "Al-Adnan", "Al-Marwan", "Al-Rashid", "Al-Majid", "Al-Sami", "Al-Ammar", "Qasem",
    "Mansour", "Fahad", "Nasser", "Salem", "Badr", "Mazen", "Ghassan", "Tawfiq", "Aziz", "Habib",
    "Khoury", "Hamdan", "Zaidan", "Sabbagh", "Nassar", "Jabr", "Darwish", "Assaf", "Farah", "Haddad"
]

SAMPLE_MESSAGES = [
    "",  # Empty messages
]

SAMPLE_STORIES = [
    "College friend and longtime companion.",
    "Childhood neighbor who became family.",
    "Work colleague and close friend.",
    "High school friend with great memories.",
    "Family friend for many years.",
    "Travel companion and adventure buddy.",
    "Book club member and literature enthusiast.",
    "Gym partner and fitness enthusiast.",
    "Art class friend with creative spirit.",
    "Music lover and concert companion.",
    "Hiking buddy and nature enthusiast.",
    "Tech professional and gaming friend.",
    "Volunteer coordinator in the community.",
    "Culinary enthusiast and dinner host.",
    "Yoga instructor and wellness advocate.",
    "Professional mentor and guide.",
    "Sports fan and weekend athlete.",
    "Gardening enthusiast with green thumb.",
    "Film enthusiast and movie companion.",
    "Dance partner and music lover."
]

SAMPLE_ABOUT = [
    "College roommate and lifelong friend who loves adventure and good coffee.",
    "Childhood friend from the neighborhood who became like family over the years.",
    "Work colleague turned close friend who shares a passion for photography.",
    "High school buddy who always brings laughter and positive energy everywhere.",
    "Family friend who has been part of our lives for as long as I can remember.",
    "Travel companion and fellow foodie who loves exploring new cuisines.",
    "Book club member and fellow literature enthusiast with great taste in novels.",
    "Gym buddy and fitness enthusiast who motivates everyone to stay healthy.",
    "Art class friend who creates beautiful paintings and has an eye for beauty.",
    "Music lover and concert buddy who knows all the best venues in town.",
    "Hiking enthusiast and nature lover who finds peace in the great outdoors.",
    "Tech professional and gaming friend who always has the latest gadgets.",
    "Volunteer coordinator who dedicates time to helping the local community.",
    "Chef and cooking enthusiast who makes the most amazing dinner parties.",
    "Yoga instructor and wellness advocate who brings calm to any situation.",
    "Professional mentor who has guided my career and personal growth.",
    "Sports fan and weekend athlete who never misses a good game.",
    "Gardening enthusiast who grows the most beautiful flowers and vegetables.",
    "Film buff and movie critic who always recommends the best entertainment.",
    "Dance partner and music teacher who brings rhythm to every celebration."
]

def generate_phone():
    """Generate a realistic phone number."""
    return f"+1-{random.randint(200, 999)}-{random.randint(200, 999)}-{random.randint(1000, 9999)}"

def generate_table():
    """Generate a table number only (no seat number)."""
    table = random.randint(1, 10)  # 10 tables for 50 guests
    return f"Table {table}"

def generate_visit_time():
    """Generate a realistic visit time within the last few hours."""
    base_time = datetime.now()
    hours_ago = random.randint(1, 6)
    minutes_ago = random.randint(0, 59)
    return base_time - timedelta(hours=hours_ago, minutes=minutes_ago)

def create_sample_guests():
    """Create sample guest data"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL not found in environment variables")
        return False
    
    # Convert async URL to sync URL for SQLAlchemy
    sync_database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
    
    print(f"Connecting to database: {sync_database_url}")
    
    try:
        # Create sync engine
        engine = create_engine(sync_database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        print("Creating 50 sample guest records...")
        
        # Clear existing data
        session.query(Guest).delete()
        session.commit()
        print("Cleared existing guest data")
        
        # Get or create relation types
        relation_types = {}
        for rel_name in ["Bride's Family", "Groom's Family", "Close Friends", "Friends", "Colleagues"]:
            rel_type = session.query(RelationType).filter_by(name=rel_name).first()
            if not rel_type:
                rel_type = RelationType(name=rel_name, description=f"{rel_name} relation")
                session.add(rel_type)
                session.flush()
            relation_types[rel_name] = rel_type
        
        session.commit()
        print(f"Created/verified {len(relation_types)} relation types")
        
        # List of relation descriptions
        relations = [
            "Uncle", "Aunt", "Cousin", "Nephew", "Niece",
            "Childhood friend", "College friend", "Work colleague", "Neighbor", "Classmate",
            "Family relative", "Close friend", "Former teacher", "Former colleague"
        ]
        
        # Create 50 sample guests
        for i in range(50):
            guest = Guest(
                first_name=random.choice(FIRST_NAMES),
                last_name=random.choice(LAST_NAMES),
                phone=generate_phone() if random.random() > 0.3 else None,  # 70% have phones
                seat_number=generate_table(),  # Always assign a table
                relation=random.choice(relations) if random.random() > 0.4 else None,  # 60% have relations
                relation_type_id=random.choice(list(relation_types.values())).id if random.random() > 0.3 else None,  # 70% have relation types
                message=None,  # Empty messages
                story=random.choice(SAMPLE_STORIES) if random.random() > 0.6 else None,  # 40% have stories
                about=random.choice(SAMPLE_ABOUT) if random.random() > 0.7 else None,  # 30% have about
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            session.add(guest)
            
            if (i + 1) % 10 == 0:
                print(f"Created {i + 1} guests...")
        
        session.commit()
        session.close()
        
        print("✅ Successfully created 50 sample guest records!")
        return True
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        return False

def main():
    """Main seeding function"""
    print("🌱 Starting database seeding...")
    
    success = create_sample_guests()
    
    if success:
        print("✅ Database seeding completed successfully!")
        print("📊 Summary:")
        print("   - 50 sample guests created with Arabic names")
        print("   - Mixed relation types (70% have relation types)")
        print("   - Relations: 60% have relation descriptions")
        print("   - All guests assigned to tables (Table 1-10)")
        print("   - Random phone numbers (70% coverage)")
        print("   - Empty messages, stories (40%), and about info (30%)")
        sys.exit(0)
    else:
        print("❌ Database seeding failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
