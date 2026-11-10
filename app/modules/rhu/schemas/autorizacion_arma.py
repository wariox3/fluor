from datetime import date

from pydantic import BaseModel


class AutorizacionArmaPortalResponse(BaseModel):
    """Empleado del cliente con las fechas que exige la autorización para portar armas."""

    codigo_empleado_pk: int
    numero_identificacion: str | None = None
    nombre_corto: str | None = None
    cargo_nombre: str | None = None
    fecha_acreditacion: date | None = None
    fecha_poligono: date | None = None
    fecha_psicofisico: date | None = None
    # Acreditación, polígono y psicofísico vigentes hoy: entra en "imprimir todos"
    vigente: bool


class AutorizacionArmaPortalListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[AutorizacionArmaPortalResponse]
