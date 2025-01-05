import logging
from flask import (
    Flask,
    jsonify
)
from flask_pymongo import PyMongo
from http import HTTPStatus


# Import Settings
from settings import get_config

# Creating Flask App
app = Flask(__name__)
logger = logging.getLogger(__name__)

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
