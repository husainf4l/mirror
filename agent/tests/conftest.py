import pytest
import sys
import os
import asyncio

# Add the parent directory to Python path for all tests
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_api_base():
    """Fixture for mock API base URL"""
    return "http://test.example.com/api"