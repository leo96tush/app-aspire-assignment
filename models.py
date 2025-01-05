from datetime import datetime
from bson.objectid import ObjectId

class Tweet:
    def __init__(self, user_id, text):
        self.user_id = user_id
        self.text = text
        self.created_at = datetime.utcnow()

    def save(self, mongo):
        """Save the tweet to the MongoDB database."""
        tweet_data = {
            "user_id": self.user_id,
            "text": self.text,
            "created_at": self.created_at
        }
        # Insert the tweet data into the 'tweets' collection and return the inserted ID
        result = mongo.db.tweets.insert_one(tweet_data)
        return result.inserted_id

    @staticmethod
    def get_all(mongo):
        """Get all tweets from the MongoDB database."""
        tweets_cursor = mongo.db.tweets.find()
        tweets = []
        for tweet in tweets_cursor:
            tweet['_id'] = str(tweet['_id'])  # Convert ObjectId to string for JSON serialization
            tweets.append(tweet)
        return tweets


# Define the User model class
class User:
    def __init__(self, username, email, following=None):
        self.username = username
        self.email = email
        self.created_at = datetime.utcnow()
        self.following = following if following is not None else []

    def save(self, mongo):
        """Save the user to the MongoDB database."""
        user_data = {
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at,
            "following": self.following
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
            if 'following' in user:
                user['following'] = [str(follow_id) for follow_id in user['following']]
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
