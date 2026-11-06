import hashlib
import httpx
import logging
from app.core.config import B2_KEY_ID, B2_APPLICATION_KEY, B2_BUCKET_NAME
import base64
import threading
import time

logger = logging.getLogger(__name__)

# Respuestas de B2 que se resuelven pidiendo una URL de subida nueva y reintentando
# (guía "Integration Checklist" de Backblaze). 400/403/404 son errores de datos, permisos o cuota.
REINTENTABLES = {401, 408, 429, 500, 503}
MAX_ESPERA_REINTENTO = 5  # segundos


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

    def _invalidar_autorizacion(self):
        """Fuerza autenticar de nuevo en la próxima llamada (token de cuenta vencido o revocado)."""
        with self._lock:
            self._token_expires = 0

    @staticmethod
    def _espera(response: httpx.Response | None, intento: int) -> float:
        """Segundos antes del siguiente intento: Retry-After si B2 lo envía, si no 1s, 2s, 4s..."""
        retry_after = response.headers.get("Retry-After") if response is not None else None
        if retry_after and retry_after.isdigit():
            return min(int(retry_after), MAX_ESPERA_REINTENTO)
        return min(2 ** (intento - 1), MAX_ESPERA_REINTENTO)

    def upload_file(self, file_path: str, data: bytes, content_type: str, intentos: int = 3) -> None:
        sha1 = hashlib.sha1(data).hexdigest()
        for intento in range(1, intentos + 1):
            try:
                self._ensure_authorized()
                # Cada intento usa una URL de subida nueva, como pide B2 tras un fallo
                response = httpx.post(
                    f"{self._api_url}/b2api/v3/b2_get_upload_url",
                    headers={"Authorization": self._auth_token},
                    json={"bucketId": self._get_bucket_id()},
                    timeout=15,
                )
                if response.status_code == 401:
                    self._invalidar_autorizacion()
                if response.is_success:
                    upload_data = response.json()
                    response = httpx.post(
                        upload_data["uploadUrl"],
                        headers={
                            "Authorization": upload_data["authorizationToken"],
                            "X-Bz-File-Name": file_path,
                            "Content-Type": content_type,
                            "Content-Length": str(len(data)),
                            "X-Bz-Content-Sha1": sha1,
                        },
                        content=data,
                        timeout=120,
                    )
                    if response.is_success:
                        return
                if response.status_code not in REINTENTABLES or intento == intentos:
                    response.raise_for_status()
                motivo = f"HTTP {response.status_code}"
                espera = self._espera(response, intento)
            except (httpx.TimeoutException, httpx.TransportError) as e:
                if intento == intentos:
                    raise
                motivo = type(e).__name__
                espera = self._espera(None, intento)
            logger.warning("Reintentando subida a B2 de %s (intento %s de %s, %s): espera %ss",
                           file_path, intento + 1, intentos, motivo, espera)
            time.sleep(espera)

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

    def get_download_url(self, file_path: str) -> str:
        self._ensure_authorized()
        return f"{self._download_url}/file/{B2_BUCKET_NAME}/{file_path}?Authorization={self._auth_token}"


b2_client = BackblazeB2()
