import logging
from flask import (
    Flask,
    jsonify
)
from flask_pymongo import PyMongo
from http import HTTPStatus


# Import Settings and Logger
from settings import get_config
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
db = mongo.db

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
