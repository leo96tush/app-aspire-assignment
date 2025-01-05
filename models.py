from datetime import datetime
from bson.objectid import ObjectId

class Tweet:
    def __init__(self, text, user_id):
        self.text = text
        self.user_id = user_id
        self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            "text": self.text,
            "user_id": self.user_id,
            "created_at": self.created_at
        }


# Define the User model class
class User:
    def __init__(self, username, email):
        self.username = username
        self.email = email
        self.created_at = datetime.utcnow()

    def save(self, mongo):
        """Save the user to the MongoDB database."""
        user_data = {
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at
        }
        # Insert the user data into the 'users' collection and return the inserted ID
        result = mongo.db.users.insert_one(user_data)
        return result.inserted_id

    @staticmethod
    def get_all(mongo):
        """Get all users from the MongoDB database."""
        users_cursor = mongo.db.users.find()
        users = []
        for user in users_cursor:
            user['_id'] = str(user['_id'])  # Convert ObjectId to string for JSON serialization
            users.append(user)
        return users

    @staticmethod
    def get_by_id(user_id, mongo):
        """Get a user by their ID."""
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if user:
            user['_id'] = str(user['_id'])  # Convert ObjectId to string
            return user
        return None
