# ASPIRE ASSIGNMENT
# Backend API with Flask and MongoDB

## Overview

This backend API is built using Flask, a lightweight Python web framework, and MongoDB, a NoSQL database. It provides a set of endpoints that allow you to interact with data stored in MongoDB.

## Features

- RESTful API design with support for common CRUD operations.
- Data is stored in MongoDB, providing flexible and scalable document storage.
- Authentication and authorization (optional, e.g., using JWT tokens).
- Optionally, includes other features like logging, validation, or email notifications.

## Technologies

- **Flask**: Python web framework for building the API.
- **MongoDB**: NoSQL database for storing data.
- **Flask-PyMongo**: Flask extension for working with MongoDB.

## Requirements

Before you start, ensure you have the following installed:

- Python 3.10.12
- pip (Python package installer)
- MongoDB (running locally or using a cloud service like MongoDB Atlas)

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/leo96tush/app-aspire-assignment.git
cd app-aspire-assignment
```
### 2. Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate 
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up MongoDB
- If you are using a local MongoDB instance, ensure MongoDB is installed and running on your machine.
Alternatively, set up a MongoDB Atlas cluster and get your connection URI.

### 5. Configure environment variables
```bash
FLASK_APP=app.py
FLASK_ENV=development
MONGO_URI=mongodb://localhost:27017/your_database_name   # Change this for MongoDB Atlas URI
```

### 6. Run the application
```bash
flask run
```
The API should now be accessible at http://127.0.0.1:5000.

## API Endpoints

### 1. `POST /tweets`

Create a new tweet.

#### Request Body:
The request body should contain the following fields:
- **user_id** (string, required): The ID of the user who is creating the tweet.
- **text** (string, required): The content of the tweet.

##### Example Request:
```json
{
    "user_id": "60c72b2f9b1d8a1f6c8d879e",
    "text": "This is my first tweet!"
}
```

#### Response:
- **201 Created**: If the tweet is successfully created, returns a JSON response with the tweet details.
- **400 Bad Request**: If either user_id or text is missing, returns an error message.
- **404 Not Found**: If the provided user_id does not exist, returns an error message indicating that the user was not found.
- **500 Internal Server Error**: If there is an internal server error while creating the tweet.

#### Success Response Example:
```json
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
```

#### Error Response Example (Missing Fields):
If either `user_id` or `text` is missing in the request
```json
{
    "status": "error",
    "message": "User ID and tweet text are required",
    "error": {
        "code": 400,
        "details": "Both 'user_id' and 'text' are required in the request"
    },
    "code": 400
}
```

#### Error Response Example (User Not Found):
If the provided `user_id` does not exist
```json
{
    "status": "error",
    "message": "User not found",
    "error": {
        "code": 404,
        "details": "User with ID 60c72b2f9b1d8a1f6c8d879e not found"
    },
    "code": 404
}
```

#### Error Response Example (Server Error):
If an internal server error occurs during tweet creation
```json
{
    "status": "error",
    "message": "Error creating tweet",
    "error": {
        "code": 500,
        "details": "<exception details>"
    },
    "code": 500
}
```

### 2. `POST /users/<user_id>/follow`

Follow a user.

Allows the current user to follow another user by creating a relationship where the `current_user_id` starts following the specified `user_id`.

#### Request Body:
The request body should contain the following field:
- **current_user_id** (string, required): The ID of the current user who wants to follow the specified user.

##### Example Request:
```json
{
    "current_user_id": "60c72b2f9b1d8a1f6c8d879f"
}
```

##### Response:
- **200 OK**: If the user is successfully followed, returns a JSON response with the user_id of the followed user.
- **400 Bad Request**: If the current_user_id is missing from the request body.
- **404 Not Found**: If either the specified user_id or the current_user_id does not exist.
- **500 Internal Server Error**: If there is an internal server error while processing the follow request.

##### Success Response Example:
```json
{
    "status": "success",
    "message": "User followed successfully",
    "data": {
        "user_id": "60c72b2f9b1d8a1f6c8d879e"
    },
    "code": 200
}
```

#### Error Response Example (Missing `current_user_id`):
If the `current_user_id` is missing from the request body
```json
{
    "status": "error",
    "message": "current_user_id is required",
    "code": 400
}
```
#### Error Response Example (User Not Found):
If the specified `user_id` or `current_user_id` does not exist
```json
{
    "status": "error",
    "message": "User or current user not found",
    "code": 404
}
```
#### Error Response Example (Server Error):
If an internal server error occurs during the follow process
```json
{
    "status": "error",
    "message": "Error following user",
    "error": {
        "code": 500,
        "details": "<exception details>"
    },
    "code": 500
}
```

### 3. `GET /users/<user_id>/timeline`

Get the timeline of tweets for a specific user.

This API retrieves the tweets from all users that the specified user is following. If the user does not exist or has not followed any users, appropriate responses are returned.

#### Parameters:
- **user_id** (string, required): The unique identifier of the user whose timeline is to be retrieved.

#### Response:
- **200 OK**: If the timeline is successfully retrieved, returns a list of tweets from followed users.
- **404 Not Found**: If the specified `user_id` does not exist.
- **200 OK**: If the user is not following anyone, returns an empty list with a success message.
- **500 Internal Server Error**: If there is an internal server error while fetching the timeline.

##### Success Response Example (Timeline Retrieved):
```json
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
```
#### Success Response Example (No Users Followed):
```json
{
    "status": "success",
    "message": "No users followed yet",
    "data": [],
    "code": 200
}
```
#### Error Response Example (User Not Found):
If the specified `user_id` does not exist
```json
{
    "status": "error",
    "message": "User not found",
    "code": 404
}
```
#### Error Response Example (Server Error):
If an internal server error occurs while fetching the timeline
```json
{
    "status": "error",
    "message": "Error fetching timeline",
    "error": {
        "code": 500,
        "details": "<exception details>"
    },
    "code": 500
}
```
