import logging
from pathlib import Path

import requests
from yaml import safe_load


def get_host_config(fn: str | None = None):
    path = Path(fn) if fn else Path.home() / ".mdhosts"

    if not path.is_file():
        return {"hosts": {}, "missing_host_config": str(path)}

    with path.open("rt") as f:
        host_details = safe_load(f)

    return host_details


class Locu:
    def __init__(self, url: str):
        self.api_base = url.rstrip("/")

        if not self.api_base.endswith("/api"):
            self.api_base = f"{self.api_base}/api"

    def get(self, path: str):
        try:
            endpoint = f"{self.api_base}/{path}"
            logging.info(f"GET: {endpoint}")
            response = requests.get(endpoint)
            return response.json()

        except requests.exceptions.RequestException as e:
            logging.error(f"HTTP ERROR: {e}")
            sys.exit(1)

    def post(self, path: str, payload: dict):
        try:
            endpoint = f"{self.api_base}/{path}"
            logging.info(f"POST: {endpoint}")
            response = requests.post(endpoint, json=payload)
            response.raise_for_status()
            logging.info(response)
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"HTTP ERROR: {e}")
            sys.exit(1)
