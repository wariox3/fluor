from datetime import date, datetime, timedelta, timezone

from app.core.config import DB_TIME_ZONE

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
