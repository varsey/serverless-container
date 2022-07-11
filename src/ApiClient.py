import json
import requests
from requests.auth import HTTPBasicAuth


class ApiClient:
    @staticmethod
    def send_payload(payload, endpoint: str, user: str, passw: str):
        response = requests.post(
            endpoint,
            data=json.dumps(payload),
            auth=HTTPBasicAuth(user, passw)
        )

        return response
