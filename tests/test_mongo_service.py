import pytest
from src.services.mongo_service import MongoService
from src.config import settings

@pytest.mark.asyncio
async def test_mongo_connection():
    """
    Tests the connection to the MongoDB database by calling the ping method.
    """
    # Initialize the service with the connection string from settings
    mongo_service = MongoService(connection_string=settings.MONGO_DB_CONNECTION_STRING)
    
    # Check the connection
    is_connected = mongo_service.ping()
    
    # Assert that the connection was successful
    assert is_connected, "Failed to connect to MongoDB."
