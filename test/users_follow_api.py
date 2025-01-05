import pytest
from unittest.mock import patch
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from flask import Flask, jsonify, request
from http import HTTPStatus


@pytest.fixture
def client():
    app = Flask(__name__)
    mongo = PyMongo(app)

    @app.route('/users/<user_id>/follow', methods=['POST'])
    def follow_user(user_id):
        try:
            current_user_id = request.json.get('current_user_id')

            if not current_user_id:
                return jsonify(create_api_response(
                    status="error",
                    message="current_user_id is required",
                    code=HTTPStatus.BAD_REQUEST
                )), HTTPStatus.BAD_REQUEST

            user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
            current_user = mongo.db.users.find_one({"_id": ObjectId(current_user_id)})

            if not user or not current_user:
                return jsonify(create_api_response(
                    status="error",
                    message="User or current user not found",
                    code=HTTPStatus.NOT_FOUND
                )), HTTPStatus.NOT_FOUND

            result = mongo.db.users.update_one(
                {"_id": ObjectId(current_user_id)},
                {"$addToSet": {"following": ObjectId(user_id)}}
            )

            if result.modified_count == 1:
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


# Test Case 1: Successful Follow (Valid current_user_id and user_id)
def test_follow_user_success(client):
    current_user_id = 'valid_current_user_id'
    user_id_to_follow = 'valid_user_id_to_follow'

    # Mock database find and update
    with patch('mongo.db.users.find_one') as mock_find, patch('mongo.db.users.update_one') as mock_update:
        mock_find.return_value = {'_id': user_id_to_follow}
        mock_update.return_value.modified_count = 1

        response = client.post(
            f'/users/{user_id_to_follow}/follow',
            json={'current_user_id': current_user_id}
        )

    assert response.status_code == 200
    assert response.json['status'] == 'success'
    assert response.json['message'] == 'User followed successfully'
    assert response.json['data']['user_id'] == user_id_to_follow


# Test Case 2: Missing current_user_id in Request Body
def test_follow_user_missing_current_user_id(client):
    user_id_to_follow = 'valid_user_id_to_follow'

    response = client.post(
        f'/users/{user_id_to_follow}/follow',
        json={}  # Missing current_user_id
    )

    assert response.status_code == 400
    assert response.json['status'] == 'error'
    assert response.json['message'] == 'current_user_id is required'


# Test Case 3: User or Current User Not Found (Invalid User ID)
def test_follow_user_user_not_found(client):
    current_user_id = 'valid_current_user_id'
    invalid_user_id = 'invalid_user_id'

    # Mock database to return None for invalid user
    with patch('mongo.db.users.find_one') as mock_find:
        mock_find.side_effect = [None, {'_id': current_user_id}]  # User not found, but current_user found

        response = client.post(
            f'/users/{invalid_user_id}/follow',
            json={'current_user_id': current_user_id}
        )

    assert response.status_code == 404
    assert response.json['status'] == 'error'
    assert response.json['message'] == 'User or current user not found'


# Test Case 4: Failed to Follow User (DB Update Error)
def test_follow_user_failed_to_follow(client):
    current_user_id = 'valid_current_user_id'
    user_id_to_follow = 'valid_user_id_to_follow'

    # Mock database to simulate failed update (no modifications)
    with patch('mongo.db.users.find_one') as mock_find, patch('mongo.db.users.update_one') as mock_update:
        mock_find.return_value = {'_id': user_id_to_follow}
        mock_update.return_value.modified_count = 0  # Simulate failure

        response = client.post(
            f'/users/{user_id_to_follow}/follow',
            json={'current_user_id': current_user_id}
        )

    assert response.status_code == 500
    assert response.json['status'] == 'error'
    assert response.json['message'] == 'Failed to follow user'


# Test Case 5: Internal Server Error (Exception During Processing)
def test_follow_user_internal_error(client):
    current_user_id = 'valid_current_user_id'
    user_id_to_follow = 'valid_user_id_to_follow'

    # Simulate an exception during the API call
    with patch('mongo.db.users.find_one', side_effect=Exception("Database error")):
        response = client.post(
            f'/users/{user_id_to_follow}/follow',
            json={'current_user_id': current_user_id}
        )

    assert response.status_code == 500
    assert response.json['status'] == 'error'
    assert response.json['message'] == 'Error following user'
    assert 'details' in response.json['error']


# Test Case 6: Invalid `current_user_id` Format
def test_follow_user_invalid_current_user_id_format(client):
    invalid_user_id = 'invalid_user_id_format'
    user_id_to_follow = 'valid_user_id_to_follow'

    # Mock database to return None for invalid user format
    with patch('mongo.db.users.find_one') as mock_find:
        mock_find.side_effect = [None, {'_id': invalid_user_id}]  # current_user_id is invalid

        response = client.post(
            f'/users/{user_id_to_follow}/follow',
            json={'current_user_id': invalid_user_id}
        )

    assert response.status_code == 404
    assert response.json['status'] == 'error'
    assert response.json['message'] == 'User or current user not found'
