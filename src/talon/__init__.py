import logging
import sys
from pathlib import Path

import requests
from yaml import safe_load

logger = logging.getLogger(__name__)


def get_host_config(fn: str | None = None):
    path = Path(fn) if fn else Path.home() / ".mdhosts"

    if not path.is_file():
        return {"hosts": {}, "missing_host_config": str(path)}

    with path.open("rt") as f:
        host_details = safe_load(f)

    return host_details


class Locu:
    def __init__(self, url: str, token: str):
        self.api_base = url.rstrip("/")
        self.token = token

        if not self.api_base.endswith("/api"):
            self.api_base = f"{self.api_base}/api"

    def get(self, path: str):
        try:
            endpoint = f"{self.api_base}/{path}"
            logger.info(f"GET: {endpoint}")
            response = requests.get(
                endpoint,
                headers={"Authorization": f"Bearer {self.token}"},
            )
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP ERROR: {e}")
            sys.exit(1)

    def post(self, path: str, payload: dict):
        response = None
        endpoint = f"{self.api_base}/{path}"
        try:
            logger.info(f"POST: {endpoint}")
            response = requests.post(
                endpoint,
                json=payload,
                headers={"Authorization": f"Bearer {self.token}"},
            )
            response.raise_for_status()
            logger.info(response)
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response is not None:
                err = e.response.json()
                if "message" in err:
                    logger.error(err["message"])
                else:
                    logger.error(f"HTTP ERROR: {e}")
            else:
                err = f"No response received from {endpoint}"
            sys.exit(1)
        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP ERROR: {e}")
            sys.exit(1)
