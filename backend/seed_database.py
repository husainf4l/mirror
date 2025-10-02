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

# Sample data for generating realistic guest records
FIRST_NAMES = [
    "Alice", "Bob", "Carol", "David", "Emma", "Frank", "Grace", "Henry", "Iris", "Jack",
    "Kate", "Liam", "Maya", "Noah", "Olivia", "Peter", "Quinn", "Rachel", "Sam", "Tina",
    "Uma", "Victor", "Wendy", "Xavier", "Yara", "Zoe", "Alex", "Beth", "Chris", "Dana",
    "Ethan", "Fiona", "George", "Hannah", "Ian", "Julia", "Kyle", "Luna", "Mark", "Nina",
    "Oscar", "Penny", "Ryan", "Sarah", "Tom", "Vera", "Will", "Xara", "Yvonne", "Zack"
]

LAST_NAMES = [
    "Anderson", "Brown", "Clark", "Davis", "Evans", "Foster", "Garcia", "Harris", "Irwin", "Johnson",
    "Kelly", "Lopez", "Miller", "Nelson", "O'Connor", "Parker", "Quinn", "Rodriguez", "Smith", "Taylor",
    "Underwood", "Valdez", "Wilson", "Young", "Zhang", "Adams", "Baker", "Carter", "Douglas", "Edwards",
    "Fisher", "Green", "Hall", "Jackson", "King", "Lee", "Martin", "Moore", "Phillips", "Roberts",
    "Scott", "Thompson", "Turner", "Walker", "White", "Allen", "Bell", "Cooper", "Hill", "Lewis"
]

SAMPLE_MESSAGES = [
    "Congratulations on your special day! Wishing you a lifetime of love and happiness.",
    "So happy to celebrate with you both! Your love story is truly inspiring.",
    "May your marriage be filled with joy, laughter, and endless adventures together.",
    "Cheers to the beautiful couple! Can't wait to see what the future holds for you.",
    "Your wedding day is absolutely perfect, just like your love for each other.",
    "Wishing you both all the happiness in the world as you start this new chapter.",
    "What a beautiful ceremony! Your love shines so brightly today.",
    "Congratulations! May your love continue to grow stronger with each passing year.",
    "So grateful to witness your union. You two are meant to be together!",
    "Here's to a lifetime of beautiful moments and cherished memories together.",
    "Your love story gives us all hope. Congratulations on your wedding day!",
    "May your marriage be everything you've dreamed of and more.",
    "Sending you both love and best wishes for a wonderful future together.",
    "What a joy to celebrate your love today! Congratulations to the happy couple.",
    "Your wedding is absolutely magical. Wishing you endless happiness together.",
    "Congratulations on finding your perfect match! Your love is beautiful to witness.",
    "May your journey together be filled with love, laughter, and wonderful adventures.",
    "So excited to celebrate this special moment with you. Congratulations!",
    "Your love story is one for the ages. Wishing you a beautiful marriage.",
    "Here's to love, laughter, and your happily ever after!"
]

SAMPLE_STORIES = [
    "I remember when you first told me about your partner - your face just lit up with joy!",
    "We've been friends since college, and I've never seen you happier than you are today.",
    "Your love story reminded me that fairytales do come true. Thank you for showing us that.",
    "I had the privilege of watching your relationship blossom from the very beginning.",
    "The way you two look at each other still gives me butterflies - pure magic!",
    "I knew you were 'the one' the moment I saw how they made you laugh.",
    "Your first date story never gets old - I love how nervous you both were!",
    "Watching you two together has taught me what true partnership looks like.",
    "I'm so grateful to have witnessed your journey from friends to soulmates.",
    "Your proposal story still makes me cry happy tears every time I hear it!",
    "The way you support each other through everything is truly inspirational.",
    "I love how you both bring out the best in each other every single day.",
    "Your relationship has shown me what it means to love unconditionally.",
    "From your first dance to today's first dance - what a beautiful journey!",
    "I'm honored to call you both family and to be here celebrating with you.",
    "Your love has been a constant source of joy and inspiration to all of us.",
    "The adventures you've shared together are just the beginning of your story.",
    "Your kindness and love have touched so many lives, including mine.",
    "I can't wait to see all the amazing memories you'll create together.",
    "Thank you for showing us all what true love really looks like."
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

def generate_seat():
    """Generate a realistic seat number."""
    table = random.randint(1, 15)
    seat = random.randint(1, 8)
    return f"T{table}S{seat}"

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
    
    print(f"Connecting to database: {database_url}")
    
    try:
        # Create sync engine
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        print("Creating 50 sample guest records...")
        
        # Clear existing data
        session.query(Guest).delete()
        session.commit()
        print("Cleared existing guest data")
        
        # Create 50 sample guests
        for i in range(50):
            guest = Guest(
                first_name=random.choice(FIRST_NAMES),
                last_name=random.choice(LAST_NAMES),
                phone=generate_phone() if random.choice([True, False]) else None,
                seat_number=generate_seat() if random.choice([True, False]) else None,
                relation=random.choice(list(RelationType)),
                message=random.choice(SAMPLE_MESSAGES) if random.choice([True, False]) else None,
                story=random.choice(SAMPLE_STORIES) if random.choice([True, False]) else None,
                about=random.choice(SAMPLE_ABOUT) if random.choice([True, False]) else None,
                visit_time=generate_visit_time(),
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
        print("   - 50 sample guests created")
        print("   - Mixed relation types (family, close_friends, friend)")
        print("   - Random phone numbers and seat assignments")
        print("   - Variety of messages, stories, and about information")
        print("   - Visit times spread across the last few hours")
        sys.exit(0)
    else:
        print("❌ Database seeding failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
