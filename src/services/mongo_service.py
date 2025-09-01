import os
from pymongo import MongoClient
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

class MongoService:
    def __init__(self, connection_string: Optional[str] = None):
        """
        Initializes the MongoDB service, connecting to the database and
        selecting the collections.
        """
        from src.logger import logger
        if connection_string is None:
            connection_string = os.getenv("MONGO_DB_CONNECTION_STRING")
        logger.error(f"[MongoService] Valor de MONGO_DB_CONNECTION_STRING: {connection_string!r}")
        if not connection_string:
            logger.critical("[MongoService] Variável de ambiente MONGO_DB_CONNECTION_STRING não está definida!")
            raise ValueError("MONGO_DB_CONNECTION_STRING environment variable not set.")
        
        self.client = MongoClient(str(connection_string))
        self.db = self.client.get_database("klique")
        self.users_collection = self.db.get_collection("users")
        self.prompts_collection = self.db.get_collection("prompts")

    def get_user(self, uid: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a user from the database by their UID.

        Args:
            uid: The user's unique identifier.

        Returns:
            A dictionary representing the user, or None if not found.
        """
        return self.users_collection.find_one({"uid": uid})

    def create_user(self, user_data: Dict[str, Any]) -> None:
        """
        Creates a new user in the database.

        Args:
            user_data: A dictionary containing user information (e.g., uid, email).
                       Initial values for request_count and last_request_time will be set.
        """
        user_data.update({
            "request_count": 0,
            "last_request_time": datetime.utcnow(),
            "subscription_plan": "free",
            "created_at": datetime.utcnow()
        })
        self.users_collection.insert_one(user_data)

    def save_prompt(self, prompt_data: Dict[str, Any]) -> None:
        """
        Saves a new prompt to the database.

        Args:
            prompt_data: A dictionary containing prompt information 
                         (e.g., uid, text, drive_file_id).
                         A timestamp will be added automatically.
        """
        prompt_data["timestamp"] = datetime.utcnow()
        self.prompts_collection.insert_one(prompt_data)

    def check_rate_limit(self, uid: str) -> bool:
        """
        Checks if a user has exceeded the rate limit for the free plan.

        The limit is 5 requests within a 30-minute window.

        Args:
            uid: The user's unique identifier.

        Returns:
            True if the rate limit is exceeded, False otherwise.
        """
        user = self.get_user(uid)
        if not user or user.get("subscription_plan") != "free":
            return False

        last_request_time = user.get("last_request_time", datetime.min)
        request_count = user.get("request_count", 0)
        
        thirty_minutes_ago = datetime.utcnow() - timedelta(minutes=30)

        if last_request_time < thirty_minutes_ago:
            # Reset the counter if the window has passed
            self.users_collection.update_one(
                {"uid": uid},
                {"$set": {"request_count": 1, "last_request_time": datetime.utcnow()}}
            )
            return False
        
        if request_count >= 5:
            return True # Limit exceeded

        # Increment the counter
        self.users_collection.update_one(
            {"uid": uid},
            {"$inc": {"request_count": 1}}
        )
        return False

    def ping(self) -> bool:
        """
        Checks if the connection to the database is alive.

        Returns:
            True if the connection is alive, False otherwise.
        """
        try:
            self.client.admin.command('ping')
            return True
        except Exception:
            return False
