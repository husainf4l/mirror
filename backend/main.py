import os
from dotenv import load_dotenv

# Load environment variables from parent directory FIRST
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Import the FastAPI app from the new structure
from app.main import app

# This file serves as the entry point for uvicorn
# Run with: uvicorn main:app --reload
