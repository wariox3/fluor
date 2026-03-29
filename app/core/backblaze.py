import hashlib
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
        self._account_id: str | None = None
        self._bucket_id: str | None = None
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
        self._account_id = data["accountId"]
        self._api_url = data["apiInfo"]["storageApi"]["apiUrl"]
        self._auth_token = data["authorizationToken"]
        self._download_url = data["apiInfo"]["storageApi"]["downloadUrl"]
        self._token_expires = time.time() + 82800  # 23 hours
        self._bucket_id = None  # reset on re-auth

    def _ensure_authorized(self):
        if not self._auth_token or time.time() >= self._token_expires:
            with self._lock:
                if not self._auth_token or time.time() >= self._token_expires:
                    self._authorize()

    def upload_file(self, file_path: str, data: bytes, content_type: str) -> None:
        self._ensure_authorized()
        # Get upload URL
        response = httpx.post(
            f"{self._api_url}/b2api/v3/b2_get_upload_url",
            headers={"Authorization": self._auth_token},
            json={"bucketId": self._get_bucket_id()},
            timeout=15,
        )
        response.raise_for_status()
        upload_data = response.json()
        upload_url = upload_data["uploadUrl"]
        upload_token = upload_data["authorizationToken"]

        sha1 = hashlib.sha1(data).hexdigest()
        upload_response = httpx.post(
            upload_url,
            headers={
                "Authorization": upload_token,
                "X-Bz-File-Name": file_path,
                "Content-Type": content_type,
                "Content-Length": str(len(data)),
                "X-Bz-Content-Sha1": sha1,
            },
            content=data,
            timeout=120,
        )
        upload_response.raise_for_status()

    def _get_bucket_id(self) -> str:
        if self._bucket_id:
            return self._bucket_id
        response = httpx.post(
            f"{self._api_url}/b2api/v3/b2_list_buckets",
            headers={"Authorization": self._auth_token},
            json={"accountId": self._account_id, "bucketName": B2_BUCKET_NAME},
            timeout=15,
        )
        response.raise_for_status()
        buckets = response.json().get("buckets", [])
        if not buckets:
            raise ValueError(f"Bucket '{B2_BUCKET_NAME}' not found")
        self._bucket_id = buckets[0]["bucketId"]
        return self._bucket_id

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
