import logging
from flask import (
    Flask,
    jsonify
)
from http import HTTPStatus

from settings import get_config

app = Flask(__name__)
logger = logging.getLogger(__name__)

# Load configuration based on the FLASK_ENV environment variable
Config = get_config()
app.config.from_object(Config)

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
