import httpx
import logging
from app.core.config import ZINC_URL

logger = logging.getLogger(__name__)


class Zinc:

    def correo(self, correo: str, asunto: str, contenido: str, aplicacion = "semantica", archivos: list = []):
        url = "/api/correo/itrio"
        datos = {
            "correo": correo,
            "asunto": asunto,
            "contenido": contenido,
            "aplicacion": aplicacion,
            "archivos": archivos,
        }
        respuesta = self._post(datos, url)
        if respuesta["status"] == 200:
            return {"error": False, "status": respuesta["status"], "datos": respuesta["datos"]}
        else:
            return {"error": True, "status": respuesta["status"], "datos": respuesta["datos"]}

    def _post(self, data: dict, url: str):
        full_url = ZINC_URL + url
        try:
            response = httpx.post(full_url, json=data, timeout=10)
            return {"status": response.status_code, "datos": response.json()}
        except Exception as e:
            logger.error(f"Zinc error: {e}")
            return {"status": 500, "datos": {}}
