import httpx
from app.core.config import B2_KEY_ID, B2_APPLICATION_KEY, B2_BUCKET_NAME
import base64
import threading
import time


class BackblazeB2:
    def __init__(self):
        self._api_url: str | None = None
        self._auth_token: str | None = None
        self._download_url: str | None = None
        self._token_expires: float = 0
        self._lock = threading.Lock()

    def _authorize(self):
        credentials = base64.b64encode(
            f"{B2_KEY_ID}:{B2_APPLICATION_KEY}".encode()
        ).decode()
        response = httpx.get(
            "https://api.backblazeb2.com/b2api/v3/b2_authorize_account",
            headers={"Authorization": f"Basic {credentials}"},
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
        self._api_url = data["apiInfo"]["storageApi"]["apiUrl"]
        self._auth_token = data["authorizationToken"]
        self._download_url = data["apiInfo"]["storageApi"]["downloadUrl"]
        self._token_expires = time.time() + 82800  # 23 hours

    def _ensure_authorized(self):
        if not self._auth_token or time.time() >= self._token_expires:
            with self._lock:
                if not self._auth_token or time.time() >= self._token_expires:
                    self._authorize()

    def download_file(self, file_path: str) -> tuple[bytes, str]:
        self._ensure_authorized()
        url = f"{self._download_url}/file/{B2_BUCKET_NAME}/{file_path}"
        response = httpx.get(
            url,
            headers={"Authorization": self._auth_token},
            timeout=60,
        )
        response.raise_for_status()
        content_type = response.headers.get("content-type", "application/octet-stream")
        return response.content, content_type


b2_client = BackblazeB2()
