import logging
from flask import (
    Flask,
    jsonify,
    request
)
from flask_pymongo import PyMongo
from http import HTTPStatus


# Import Settings and Logger
from settings import get_config
from models import (
    User,
    Tweet
)
from utils.logging_setup import setup_logger


# Creating Flask App
app = Flask(__name__)

# Create Logger
logger = setup_logger()

# Load configuration dynamically
Config = get_config()
app.config.from_object(Config)

# Connect to MongoDB
mongo = PyMongo(app)


# @app.route('/tweets', methods=['POST'])
# def create_tweet():
#     try:
#         data = request.get_json()
#         user = mongo.db.users.find_one({'_id': data['user_id']})
#
#         if not user:
#             return jsonify({"error": "User not found"}), HTTPStatus.NOT_FOUND
#
#         new_tweet = Tweet(text=data['text'], user_id=data['user_id'])
#         tweet_id = mongo.db.tweets.insert_one(new_tweet.to_dict()).inserted_id
#         new_tweet = mongo.db.tweets.find_one({'_id': tweet_id})
#
#         return jsonify({
#             'id': str(new_tweet['_id']),
#             'text': new_tweet['text'],
#             'created_at': new_tweet['created_at'],
#             'user_id': new_tweet['user_id']
#         }), HTTPStatus.CREATED
#
#     except KeyError as e:
#         return jsonify({"error": f"Missing required field: {str(e)}"}), HTTPStatus.BAD_REQUEST
#     except Exception as e:
#         return jsonify({"error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR
#
#
# @app.route('/tweets/<tweet_id>', methods=['GET'])
# def get_tweet(tweet_id):
#     tweet = mongo.db.tweets.find_one({'_id': tweet_id})
#     if tweet:
#         return jsonify({
#             'id': str(tweet['_id']),
#             'text': tweet['text'],
#             'created_at': tweet['created_at'],
#             'user_id': tweet['user_id']
#         }), HTTPStatus.OK
#     return jsonify({"error": "Tweet not found"}), HTTPStatus.NOT_FOUND

def create_api_response(status, message, data=None, error=None, code=None):
    """Utility function to create a consistent API response structure."""
    response = {
        "status": status,
        "message": message,
    }

    if status == "success":
        response["data"] = data
    elif status == "error":
        response["error"] = error

    if code:
        response["code"] = code

    return response


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
