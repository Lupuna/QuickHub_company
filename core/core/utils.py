import base64
import json


def extract_payload(jwt_token):
    try:
        header, payload, signature = jwt_token.split('.')
        payload += '=' * (-len(payload) % 4)
        decoded_payload = base64.urlsafe_b64decode(payload)
        payload_data = json.loads(decoded_payload)
        return payload_data

    except (ValueError, json.JSONDecodeError):
        return {"error": "Invalid token format"}