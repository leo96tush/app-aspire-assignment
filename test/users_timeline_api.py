import pytest
from unittest.mock import patch
from flask import Flask, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from http import HTTPStatus


@pytest.fixture
def client():
    app = Flask(__name__)
    mongo = PyMongo(app)

    @app.route('/users/<user_id>/timeline', methods=['GET'])
    def get_user_timeline(user_id):
        try:
            # Simulated database call
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

            tweets_cursor = mongo.db.tweets.find({"user_id": {"$in": list(map(str, following_ids))}})
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
            return jsonify(create_api_response(
                status="error",
                message="Error fetching timeline",
                error={"code": HTTPStatus.INTERNAL_SERVER_ERROR, "details": str(e)},
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


# Test Case 1: Successful Response (User with Followers and Tweets)
def test_get_user_timeline_success_with_following_users_and_tweets(client):
    user_id = 'valid_user_id_with_following_and_tweets'
    response = client.get(f'/users/{user_id}/timeline')
    assert response.status_code == 200
    assert response.json['status'] == 'success'
    assert 'data' in response.json
    assert isinstance(response.json['data'], list)


# Test Case 2: User Not Found (Invalid `user_id`)
def test_get_user_timeline_user_not_found(client):
    user_id = 'non_existent_user_id'
    response = client.get(f'/users/{user_id}/timeline')
    assert response.status_code == 404
    assert response.json['status'] == 'error'
    assert response.json['message'] == 'User not found'


# Test Case 3: No Users Followed (Empty Following List)
def test_get_user_timeline_no_following(client):
    user_id = 'user_with_no_following'
    response = client.get(f'/users/{user_id}/timeline')
    assert response.status_code == 200
    assert response.json['status'] == 'success'
    assert response.json['message'] == 'No users followed yet'
    assert response.json['data'] == []


# Test Case 4: Server Error (Internal Server Error)
def test_get_user_timeline_internal_error(client, mocker):
    user_id = 'valid_user_id'
    # Simulate an exception in the code
    mocker.patch('mongo.db.tweets.find', side_effect=Exception('Database error'))
    response = client.get(f'/users/{user_id}/timeline')
    assert response.status_code == 500
    assert response.json['status'] == 'error'
    assert response.json['message'] == 'Error fetching timeline'


# Test Case 5: Empty Timeline (No Tweets from Followed Users)
def test_get_user_timeline_no_tweets(client):
    user_id = 'user_with_following_no_tweets'
    response = client.get(f'/users/{user_id}/timeline')
    assert response.status_code == 200
    assert response.json['status'] == 'success'
    assert response.json['message'] == 'Timeline retrieved successfully'
    assert response.json['data'] == []


# Test Case 6: Invalid `user_id` Format
def test_get_user_timeline_invalid_user_id_format(client):
    user_id = 'invalid_format_user_id'
    response = client.get(f'/users/{user_id}/timeline')
    assert response.status_code == 400
    assert response.json['status'] == 'error'
    assert response.json['message'] == 'Invalid user ID format'
