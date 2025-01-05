from flask import (
    Flask,
    jsonify,
    request
)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from http import HTTPStatus


# Import Settings and Logger
from settings import get_config
from models import (
    User,
    Tweet
)
from utils.logging_setup import setup_logger
from utils.api_response_generator import create_api_response

# Creating Flask App
app = Flask(__name__)

# Create Logger
logger = setup_logger()

# Load configuration dynamically
Config = get_config()
app.config.from_object(Config)

# Connect to MongoDB
mongo = PyMongo(app)


@app.route('/users', methods=['POST'])
def create_user():
    try:
        # Get data from the request
        username = request.json.get('username')
        email = request.json.get('email')

        # Check if the data is valid
        if not username or not email:
            error_details = {
                "code": HTTPStatus.BAD_REQUEST,
                "details": "Both 'username' and 'email' are required in the request"
            }
            return jsonify(create_api_response(
                status="error",
                message="Username and email are required",
                error=error_details,
                code=HTTPStatus.BAD_REQUEST
            )), HTTPStatus.BAD_REQUEST

        # Create a new User object
        new_user = User(username=username, email=email)

        # Save the user to the database using the User model
        user_id = new_user.save(mongo)

        # Log the creation and return the result
        logger.info(f"User {username} created with ID: {str(user_id)}")

        return jsonify(create_api_response(
            status="success",
            message="User created successfully",
            data={"user_id": str(user_id), "username": username, "email": email},
            code=HTTPStatus.CREATED
        )), HTTPStatus.CREATED

    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        error_details = {
            "code": HTTPStatus.INTERNAL_SERVER_ERROR,
            "details": str(e)
        }
        return jsonify(create_api_response(
            status="error",
            message="Error creating user",
            error=error_details,
            code=HTTPStatus.INTERNAL_SERVER_ERROR
        )), HTTPStatus.INTERNAL_SERVER_ERROR


@app.route('/users', methods=['GET'])
def get_users():
    try:
        # Fetch all users using the User model
        users = User.get_all(mongo)

        return jsonify(create_api_response(
            status="success",
            message="Users retrieved successfully",
            data=users,
            code=HTTPStatus.OK
        )), HTTPStatus.OK
    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}")
        error_details = {
            "code": HTTPStatus.INTERNAL_SERVER_ERROR,
            "details": str(e)
        }
        return jsonify(create_api_response(
            status="error",
            message="Error fetching users",
            error=error_details,
            code=HTTPStatus.INTERNAL_SERVER_ERROR
        )), HTTPStatus.INTERNAL_SERVER_ERROR


@app.route('/users/<user_id>', methods=['GET'])
def get_user_by_id(user_id):
    try:
        # Fetch a user by their ID using the User model
        user = User.get_by_id(user_id, mongo)
        if user:
            return jsonify(create_api_response(
                status="success",
                message="User retrieved successfully",
                data=user,
                code=HTTPStatus.OK
            )), HTTPStatus.OK

        error_details = {
            "code": HTTPStatus.NOT_FOUND,
            "details": f"User with ID {user_id} not found"
        }
        return jsonify(create_api_response(
            status="error",
            message="User not found",
            error=error_details,
            code=HTTPStatus.NOT_FOUND
        )), HTTPStatus.NOT_FOUND

    except Exception as e:
        logger.error(f"Error fetching user: {str(e)}")
        error_details = {
            "code": HTTPStatus.INTERNAL_SERVER_ERROR,
            "details": str(e)
        }
        return jsonify(create_api_response(
            status="error",
            message="Error fetching user",
            error=error_details,
            code=HTTPStatus.INTERNAL_SERVER_ERROR
        )), HTTPStatus.INTERNAL_SERVER_ERROR



# Create a Tweet Route
@app.route('/tweets', methods=['POST'])
def create_tweet():
    try:
        # Get data from the request
        user_id = request.json.get('user_id')
        text = request.json.get('text')

        # Validate input
        if not user_id or not text:
            error_details = {
                "code": HTTPStatus.BAD_REQUEST,
                "details": "Both 'user_id' and 'text' are required in the request"
            }
            return jsonify(create_api_response(
                status="error",
                message="User ID and tweet text are required",
                error=error_details,
                code=HTTPStatus.BAD_REQUEST
            )), HTTPStatus.BAD_REQUEST

        # Create a new Tweet object
        new_tweet = Tweet(user_id=user_id, text=text)

        # Save the tweet to the database
        tweet_id = new_tweet.save(mongo)

        # Log the creation and return the result
        logger.info(f"Tweet created with ID: {str(tweet_id)}")

        return jsonify(create_api_response(
            status="success",
            message="Tweet created successfully",
            data={"tweet_id": str(tweet_id), "user_id": user_id, "text": text},
            code=HTTPStatus.CREATED
        )), HTTPStatus.CREATED

    except Exception as e:
        logger.error(f"Error creating tweet: {str(e)}")
        error_details = {
            "code": HTTPStatus.INTERNAL_SERVER_ERROR,
            "details": str(e)
        }
        return jsonify(create_api_response(
            status="error",
            message="Error creating tweet",
            error=error_details,
            code=HTTPStatus.INTERNAL_SERVER_ERROR
        )), HTTPStatus.INTERNAL_SERVER_ERROR

# Get All Tweets
@app.route('/tweets', methods=['GET'])
def get_tweets():
    try:
        # Fetch all tweets from the database
        tweets = Tweet.get_all(mongo)

        return jsonify(create_api_response(
            status="success",
            message="Tweets retrieved successfully",
            data=tweets,
            code=HTTPStatus.OK
        )), HTTPStatus.OK
    except Exception as e:
        logger.error(f"Error fetching tweets: {str(e)}")
        error_details = {
            "code": HTTPStatus.INTERNAL_SERVER_ERROR,
            "details": str(e)
        }
        return jsonify(create_api_response(
            status="error",
            message="Error fetching tweets",
            error=error_details,
            code=HTTPStatus.INTERNAL_SERVER_ERROR
        )), HTTPStatus.INTERNAL_SERVER_ERROR

# Follow User Route
@app.route('/users/<user_id>/follow', methods=['POST'])
def follow_user(user_id):
    try:
        # Get the current user id from the request
        current_user_id = request.json.get('current_user_id')

        if not current_user_id:
            return jsonify(create_api_response(
                status="error",
                message="current_user_id is required",
                code=HTTPStatus.BAD_REQUEST
            )), HTTPStatus.BAD_REQUEST

        # Check if the user and current_user exist
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        current_user = mongo.db.users.find_one({"_id": ObjectId(current_user_id)})

        if not user or not current_user:
            return jsonify(create_api_response(
                status="error",
                message="User or current user not found",
                code=HTTPStatus.NOT_FOUND
            )), HTTPStatus.NOT_FOUND

        # Add the follow relationship (current_user_id follows user_id)
        result = mongo.db.users.update_one(
            {"_id": ObjectId(current_user_id)},
            {"$addToSet": {"following": ObjectId(user_id)}}
        )

        if result.modified_count == 1:
            logger.info(f"User {current_user_id} started following user {user_id}")
            return jsonify(create_api_response(
                status="success",
                message="User followed successfully",
                data={"user_id": user_id},
                code=HTTPStatus.OK
            )), HTTPStatus.OK
        else:
            return jsonify(create_api_response(
                status="error",
                message="Failed to follow user",
                code=HTTPStatus.INTERNAL_SERVER_ERROR
            )), HTTPStatus.INTERNAL_SERVER_ERROR

    except Exception as e:
        logger.error(f"Error following user: {str(e)}")
        error_details = {
            "code": HTTPStatus.INTERNAL_SERVER_ERROR,
            "details": str(e)
        }
        return jsonify(create_api_response(
            status="error",
            message="Error following user",
            error=error_details,
            code=HTTPStatus.INTERNAL_SERVER_ERROR
        )), HTTPStatus.INTERNAL_SERVER_ERROR

# Get timeline route
@app.route('/users/<user_id>/timeline', methods=['GET'])
def get_user_timeline(user_id):
    try:
        # Get the tweets from users that the user follows
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})

        if not user:
            return jsonify(create_api_response(
                status="error",
                message="User not found",
                code=HTTPStatus.NOT_FOUND
            )), HTTPStatus.NOT_FOUND

        following_ids = user.get('following', [])
        if not following_ids:
            return jsonify(create_api_response(
                status="success",
                message="No users followed yet",
                data=[],
                code=HTTPStatus.OK
            )), HTTPStatus.OK

        # Fetch tweets from all followed users
        tweets_cursor = mongo.db.tweets.find({"user_id": {"$in": following_ids}})
        tweets = []
        for tweet in tweets_cursor:
            tweet['_id'] = str(tweet['_id'])  # Convert ObjectId to string
            tweets.append(tweet)

        return jsonify(create_api_response(
            status="success",
            message="Timeline retrieved successfully",
            data=tweets,
            code=HTTPStatus.OK
        )), HTTPStatus.OK

    except Exception as e:
        logger.error(f"Error fetching timeline: {str(e)}")
        error_details = {
            "code": HTTPStatus.INTERNAL_SERVER_ERROR,
            "details": str(e)
        }
        return jsonify(create_api_response(
            status="error",
            message="Error fetching timeline",
            error=error_details,
            code=HTTPStatus.INTERNAL_SERVER_ERROR
        )), HTTPStatus.INTERNAL_SERVER_ERROR


@app.route('/ping', methods=['GET'])
def health_check():
    response = {
        "status": "success",
        "message": "pong",
        "data": None
    }
    return jsonify(response), HTTPStatus.OK

if __name__ == '__main__':
    app.run(debug=app.config.get('DEBUG'))
