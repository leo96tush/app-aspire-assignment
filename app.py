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
    """
    Create a new user.

    This API endpoint creates a new user in the system based on the provided
    username and email.

    Request Body:
        - username (str): The desired username of the user (required).
        - email (str): The email address of the user (required).

    Returns:
        flask.Response: A JSON response containing:
            - status (str): "success" or "error".
            - message (str): A brief description of the response.
            - data (dict, optional): Details of the created user if the request is successful.
                Includes:
                - user_id (str): The unique identifier of the user.
                - username (str): The username of the user.
                - email (str): The email of the user.
            - error (dict, optional): Error details if the request fails.
            - code (int): The HTTP status code.

    Raises:
        Exception: If an internal server error occurs while creating the user.

    Example:
        POST /users
        Request Body:
        {
            "username": "johndoe",
            "email": "john.doe@example.com"
        }
        Success Response:
        {
            "status": "success",
            "message": "User created successfully",
            "data": {
                "user_id": "60c72b2f9b1d8a1f6c8d879e",
                "username": "johndoe",
                "email": "john.doe@example.com"
            },
            "code": 201
        }

    Example (Error - Validation):
        POST /users
        Request Body:
        {
            "username": "johndoe"
        }

        Error Response:
        {
            "status": "error",
            "message": "Username and email are required",
            "error": {
                "code": 400,
                "details": "Both 'username' and 'email' are required in the request"
            },
            "code": 400
        }

    Example (Error - Server Error):
        POST /users
        Error Response:
        {
            "status": "error",
            "message": "Error creating user",
            "error": {
                "code": 500,
                "details": "<exception details>"
            },
            "code": 500
        }
    """
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
    """
    Retrieve all users.

    This API retrieves a list of all users stored in the database.

    Returns:
        flask.Response: A JSON response containing:
            - status (str): "success" or "error".
            - message (str): A brief description of the response.
            - data (list, optional): List of users if the request is successful.
                Each user object includes:
                - _id (str): The unique identifier of the user.
                - name (str): The name of the user.
                - email (str): The email address of the user.
                - following (list): List of user IDs the user is following.
            - error (dict, optional): Error details if the request fails.
            - code (int): The HTTP status code.

    Raises:
        Exception: If an internal server error occurs while retrieving users.

    Example:
        GET /users
        Success Response:
        {
            "status": "success",
            "message": "Users retrieved successfully",
            "data": [
                {
                    "_id": "60c72b2f9b1d8a1f6c8d879e",
                    "name": "John Doe",
                    "email": "john.doe@example.com",
                    "following": ["60c72b2f9b1d8a1f6c8d879f"]
                },
                {
                    "_id": "60c72b2f9b1d8a1f6c8d879f",
                    "name": "Jane Smith",
                    "email": "jane.smith@example.com",
                    "following": []
                }
            ],
            "code": 200
        }

    Example (Error - Server Error):
        GET /users
        Error Response:
        {
            "status": "error",
            "message": "Error fetching users",
            "error": {
                "code": 500,
                "details": "<exception details>"
            },
            "code": 500
        }
    """
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
    """
    Retrieve a user by their ID.

    This API retrieves user details based on their unique identifier (`user_id`).

    Args:
        user_id (str): The unique identifier of the user to retrieve.

    Returns:
        flask.Response: A JSON response containing:
            - status (str): "success" or "error".
            - message (str): A brief description of the response.
            - data (dict, optional): The user details if the request is successful.
                - _id (str): The unique identifier of the user.
                - name (str): The name of the user.
                - email (str): The email address of the user.
                - following (list): List of user IDs the user is following.
            - error (dict, optional): Error details if the request fails.
            - code (int): The HTTP status code.

    Raises:
        Exception: If an internal server error occurs while retrieving the user.

    Example:
        GET /users/<user_id>
        Success Response:
        {
            "status": "success",
            "message": "User retrieved successfully",
            "data": {
                "_id": "60c72b2f9b1d8a1f6c8d879e",
                "name": "John Doe",
                "email": "john.doe@example.com",
                "following": ["60c72b2f9b1d8a1f6c8d879f"]
            },
            "code": 200
        }

    Example (Error - User Not Found):
        GET /users/<invalid_user_id>
        Error Response:
        {
            "status": "error",
            "message": "User not found",
            "error": {
                "code": 404,
                "details": "User with ID <invalid_user_id> not found"
            },
            "code": 404
        }

    Example (Error - Server Error):
        GET /users/<user_id>
        Error Response:
        {
            "status": "error",
            "message": "Error fetching user",
            "error": {
                "code": 500,
                "details": "<exception details>"
            },
            "code": 500
        }
    """
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
    """
    Create a new tweet.

    This API allows a user to create a new tweet by providing their user ID and the text
    message for the tweet.

    Args:

    Returns:
        flask.Response: A JSON response containing:
            - status (str): "success" or "error".
            - message (str): A brief description of the response.
            - data (dict, optional): Details of the created tweet if the request is successful, including:
                - tweet_id (str): The unique identifier of the newly created tweet.
                - user_id (str): The ID of the user who created the tweet.
                - text (str): The content of the tweet.
            - error (dict, optional): Error details if the request fails.
            - code (int): The HTTP status code.

    Raises:
        Exception: If an internal server error occurs during tweet creation.

    Example:
        POST /tweets
        Request Body:
        {
            "user_id": "60c72b2f9b1d8a1f6c8d879e",
            "text": "This is my first tweet!"
        }

        Success Response:
        {
            "status": "success",
            "message": "Tweet created successfully",
            "data": {
                "tweet_id": "60c72b2f9b1d8a1f6c8d87a1",
                "user_id": "60c72b2f9b1d8a1f6c8d879e",
                "text": "This is my first tweet!"
            },
            "code": 201
        }

    Example (Error - Missing Fields):
        POST /tweets
        Request Body:
        {
            "user_id": "60c72b2f9b1d8a1f6c8d879e"
        }

        Error Response:
        {
            "status": "error",
            "message": "User ID and tweet text are required",
            "error": {
                "code": 400,
                "details": "Both 'user_id' and 'text' are required in the request"
            },
            "code": 400
        }
    """
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
    """
    Retrieve all tweets.

    This API retrieves all tweets from the database, allowing users to view all public tweets.

    Args:

    Returns:
        flask.Response: A JSON response containing:
            - status (str): "success" or "error".
            - message (str): A brief description of the response.
            - data (list, optional): A list of tweets if the request is successful.
            - error (dict, optional): Error details if the request fails.
            - code (int): The HTTP status code.

    Raises:
        Exception: If an internal server error occurs while fetching tweets.

    Example:
        GET /tweets
        Success Response:
        {
            "status": "success",
            "message": "Tweets retrieved successfully",
            "data": [
                {
                    "_id": "60c72b2f9b1d8a1f6c8d879f",
                    "user_id": "60c72b2f9b1d8a1f6c8d879e",
                    "text": "This is a sample tweet",
                    "created_at": "2025-01-05T12:00:00Z"
                },
                {
                    "_id": "60c72b2f9b1d8a1f6c8d879g",
                    "user_id": "60c72b2f9b1d8a1f6c8d879h",
                    "text": "Another example tweet",
                    "created_at": "2025-01-04T15:30:00Z"
                }
            ],
            "code": 200
        }
    """
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
    """
    Follow a user.

    Allows the current user to follow another user by creating a relationship where
    the `current_user_id` starts following the specified `user_id`.

    Args:
        user_id (str): The unique identifier of the user to be followed.

    Returns:
        flask.Response: A JSON response containing:
            - status (str): "success" or "error".
            - message (str): A brief description of the response.
            - data (dict, optional): Contains the `user_id` of the followed user if successful.
            - error (dict, optional): Error details if the request fails.
            - code (int): The HTTP status code.

    Raises:
        Exception: If an internal server error occurs while processing the follow request.

    Example:
        POST /users/<user_id>/follow
        Request Body:
        {
            "current_user_id": "60c72b2f9b1d8a1f6c8d879f"
        }

        Success Response:
        {
            "status": "success",
            "message": "User followed successfully",
            "data": {
                "user_id": "60c72b2f9b1d8a1f6c8d879e"
            },
            "code": 200
        }
    """
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
    """
    Get the timeline of tweets for a specific user.

    This function retrieves the tweets from all users that the specified user is following.
    If the user does not exist or no users are followed, appropriate responses are returned.

    Args:
        user_id (str): The unique identifier of the user whose timeline is to be retrieved.

    Returns:
        flask.Response: A JSON response containing:
            - status (str): "success" or "error".
            - message (str): A brief description of the response.
            - data (list, optional): A list of tweets from followed users (if successful).
            - error (dict, optional): Error details if the request fails.
            - code (int): The HTTP status code.

    Raises:
        Exception: If an internal server error occurs while fetching the timeline.

    Example:
        GET /users/<user_id>/timeline
        # Success Response
        {
            "status": "success",
            "message": "Timeline retrieved successfully",
            "data": [
                {
                    "_id": "60c72b2f9b1d8a1f6c8d879f",
                    "user_id": "60c72b2f9b1d8a1f6c8d879f",
                    "text": "This is a sample tweet",
                    "created_at": "2025-01-05T12:00:00Z"
                }
            ],
            "code": 200
        }
    """
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
