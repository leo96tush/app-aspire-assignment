import pytest
from unittest.mock import patch
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from flask import Flask, jsonify, request
from http import HTTPStatus

from ..models import Tweet

@pytest.fixture
def client():
    app = Flask(__name__)
    mongo = PyMongo(app)

    @app.route('/tweets', methods=['POST'])
    def create_tweet():
        try:
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

            # Validate that the user exists
            user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
            if not user:
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

            # Create a new Tweet object
            new_tweet = Tweet(user_id=user_id, text=text)

            # Save the tweet to the database
            tweet_id = new_tweet.save(mongo)

            return jsonify(create_api_response(
                status="success",
                message="Tweet created successfully",
                data={"tweet_id": str(tweet_id), "user_id": user_id, "text": text},
                code=HTTPStatus.CREATED
            )), HTTPStatus.CREATED

        except Exception as e:
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

    with app.test_client() as client:
        yield client


def create_api_response(status, message, data=None, error=None, code=200):
    response = {
        'status': status,
        'message': message,
        'code': code,
    }
    if data:
        response['data'] = data
    if error:
        response['error'] = error
    return response


# Test Case 1: Successful Tweet Creation (Valid user_id and text)
def test_create_tweet_success(client):
    user_id = 'valid_user_id'
    tweet_text = 'This is my first tweet!'

    # Mock database to return user data
    with patch('mongo.db.users.find_one') as mock_find, patch('mongo.db.users.save') as mock_save:
        mock_find.return_value = {'_id': user_id}  # User found
        mock_save.return_value = 'new_tweet_id'  # Simulate a tweet being saved

        response = client.post(
            '/tweets',
            json={'user_id': user_id, 'text': tweet_text}
        )

    assert response.status_code == 201
    assert response.json['status'] == 'success'
    assert response.json['message'] == 'Tweet created successfully'
    assert response.json['data']['tweet_id'] == 'new_tweet_id'
    assert response.json['data']['user_id'] == user_id
    assert response.json['data']['text'] == tweet_text


# Test Case 2: Missing Fields in Request Body (e.g., missing text)
def test_create_tweet_missing_fields(client):
    user_id = 'valid_user_id'

    # Missing text field in request
    response = client.post(
        '/tweets',
        json={'user_id': user_id}
    )

    assert response.status_code == 400
    assert response.json['status'] == 'error'
    assert response.json['message'] == 'User ID and tweet text are required'
    assert 'details' in response.json['error']


# Test Case 3: User Not Found (Invalid user_id)
def test_create_tweet_user_not_found(client):
    invalid_user_id = 'invalid_user_id'
    tweet_text = 'This is my tweet!'

    # Mock database to return None for invalid user
    with patch('mongo.db.users.find_one') as mock_find:
        mock_find.return_value = None  # User not found

        response = client.post(
            '/tweets',
            json={'user_id': invalid_user_id, 'text': tweet_text}
        )

    assert response.status_code == 404
    assert response.json['status'] == 'error'
    assert response.json['message'] == 'User not found'
    assert 'details' in response.json['error']


# Test Case 4: Internal Server Error (Exception during processing)
def test_create_tweet_internal_error(client):
    user_id = 'valid_user_id'
    tweet_text = 'This is my tweet!'

    # Simulate an exception during the tweet creation
    with patch('mongo.db.users.find_one', side_effect=Exception("Database error")):
        response = client.post(
            '/tweets',
            json={'user_id': user_id, 'text': tweet_text}
        )

    assert response.status_code == 500
    assert response.json['status'] == 'error'
    assert response.json['message'] == 'Error creating tweet'
    assert 'details' in response.json['error']


# Test Case 5: Missing user_id Field in Request Body
def test_create_tweet_missing_user_id(client):
    tweet_text = 'This is my tweet!'

    # Missing user_id field in request
    response = client.post(
        '/tweets',
        json={'text': tweet_text}
    )

    assert response.status_code == 400
    assert response.json['status'] == 'error'
    assert response.json['message'] == 'User ID and tweet text are required'
    assert 'details' in response.json['error']


# Test Case 6: Empty Tweet Text
def test_create_tweet_empty_text(client):
    user_id = 'valid_user_id'
    tweet_text = ''

    # Mock database to return user data
    with patch('mongo.db.users.find_one') as mock_find:
        mock_find.return_value = {'_id': user_id}  # User found

        response = client.post(
            '/tweets',
            json={'user_id': user_id, 'text': tweet_text}
        )

    assert response.status_code == 400
    assert response.json['status'] == 'error'
    assert response.json['message'] == 'User ID and tweet text are required'
    assert 'details' in response.json['error']
