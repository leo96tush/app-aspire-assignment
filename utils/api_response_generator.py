

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