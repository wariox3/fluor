from datetime import date, datetime, timedelta, timezone
from io import BytesIO

from PIL import Image, ImageOps

from app.core.config import DB_TIME_ZONE, APP_URL, FRONTEND_URLS

_MESES = [
    "", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]


def ahora_local() -> datetime:
    """Fecha y hora actual en la zona horaria del negocio (DB_TIME_ZONE, ej. "-05:00")."""
    signo = -1 if DB_TIME_ZONE.startswith("-") else 1
    horas, minutos = DB_TIME_ZONE.lstrip("+-").split(":")
    zona = timezone(signo * timedelta(hours=int(horas), minutes=int(minutos)))
    return datetime.now(zona).replace(tzinfo=None)


def fecha_larga(d: date) -> str:
    return f"{d.day} de {_MESES[d.month]} de {d.year}"


def fmt_numero(v, separador: str = ".") -> str:
    if v is None:
        return "0"
    return f"{v:,.0f}".replace(",", separador)


def fmt_cantidad(v) -> str:
    """Cantidad sin decimales sobrantes: 1.0 → "1", 1.5 → "1.5"."""
    v = float(v or 0)
    return str(int(v)) if v.is_integer() else str(v)


def frontend_url(origin: str | None) -> str:
    """URL base del frontend que hizo la petición, para armar enlaces de correo.

    Solo acepta orígenes de FRONTEND_URLS; cualquier otro (o sin Origin) usa APP_URL,
    así un cliente no puede hacer que el correo apunte a un dominio ajeno.
    """
    if origin and origin.rstrip("/") in FRONTEND_URLS:
        return origin.rstrip("/")
    return APP_URL.rstrip("/")


def comprimir_imagen(data: bytes, lado_maximo: int = 1600, calidad: int = 60) -> bytes:
    """Convierte una foto a WebP liviano: corrige la rotación EXIF, limita el lado mayor y quita metadatos.

    Con fotos de entrega reales, 1600 px y calidad 60 dejan ~180 KB por foto (-76%) manteniendo
    legible el texto de los cumplidos. method=6 solo ahorra ~5% más y tarda el doble.
    """
    with Image.open(BytesIO(data)) as original:
        # En JPEG decodifica ya reducido (escala DCT): mucho más rápido con fotos de 12+ MP
        original.draft("RGB", (lado_maximo, lado_maximo))
        imagen = ImageOps.exif_transpose(original).convert("RGB")
    imagen.thumbnail((lado_maximo, lado_maximo), Image.LANCZOS)
    salida = BytesIO()
    imagen.save(salida, "WEBP", quality=calidad, method=4)
    return salida.getvalue()
