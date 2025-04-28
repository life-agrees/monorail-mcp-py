# utils
import json

def safe_json_response(resp):
    try:
        return resp.json()
    except (json.JSONDecodeError, ValueError):
        # Fallback to raw text if JSON is invalid
        return {"error": resp.text}
import json
from httpx import Response

def safe_json_response(resp: Response) -> dict:
    """
    Safely parse an HTTPX Response as JSON.
    If parsing fails (invalid JSON), return a dict with an 'error' key set to the raw text.

    Args:
        resp (httpx.Response): The HTTPX response object.

    Returns:
        dict: Parsed JSON or {'error': resp.text} on failure.
    """
    try:
        return resp.json()
    except (json.JSONDecodeError, ValueError):
        return {"error": resp.text}
