import inspect
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from io import BytesIO
from typing import Any, Callable, Optional

from fastapi import HTTPException, Query
from fastapi.responses import Response
from openpyxl import Workbook
from openpyxl.cell import WriteOnlyCell
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter
from PIL import Image, ImageOps
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

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


# ---------------------------------------------------------------------------
# Listados y exportación a Excel
#
# Cada recurso declara un ListaConfig con sus filtros permitidos, el orden y las
# columnas del Excel. /lista y /excel reciben los mismos filtros, así el Excel
# trae lo mismo que se ve en pantalla pero sin paginar.
# ---------------------------------------------------------------------------

def _contiene(columna, valor):
    escapado = str(valor).replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return columna.ilike(f"%{escapado}%", escape="\\")


_OPERADORES: dict[str, Callable] = {
    "eq": lambda c, v: c == v,
    "contiene": _contiene,
    "gte": lambda c, v: c >= v,
    "lte": lambda c, v: c <= v,
    # Columna datetime contra una fecha: incluye todo ese día (<= 'AAAA-MM-DD' lo cortaría a las 00:00)
    "hasta_dia": lambda c, v: c < v + timedelta(days=1),
    "in": lambda c, v: c.in_(v),
    "es_nulo": lambda c, v: c.is_(None) if v else c.isnot(None),
}


@dataclass(frozen=True)
class Filtro:
    columna: Any
    operador: str = "eq"
    tipo: Optional[type] = None  # por defecto se toma del tipo de la columna
    descripcion: Optional[str] = None

    def __post_init__(self):
        if self.operador not in _OPERADORES:
            raise ValueError(f"Operador de filtro desconocido: {self.operador}")

    def tipo_parametro(self):
        if self.operador == "es_nulo":
            return Optional[bool]
        tipo = self.tipo or self.columna.type.python_type
        return Optional[list[tipo]] if self.operador == "in" else Optional[tipo]


@dataclass
class ListaConfig:
    pk: Any
    orden: list
    filtros: dict[str, Filtro] = field(default_factory=dict)
    ordenables: dict[str, Any] = field(default_factory=dict)  # ?orden=nombre o ?orden=-nombre
    # Relaciones a precargar con joinedload (evita N+1). Se declaran como Modelo.relacion y el
    # joinedload se arma al consultar: crearlo al importar el módulo fuerza a configurar los
    # mappers antes de que estén cargados todos los modelos.
    relaciones: list = field(default_factory=list)
    relaciones_excel: list = field(default_factory=list)  # adicionales, solo para columnas del Excel
    columnas_excel: list[tuple[str, str]] = field(default_factory=list)  # (título, atributo o ruta "rel.campo")
    max_size: int = 200
    max_filas_excel: int = 50_000

    def __post_init__(self):
        self.params_lista = self._dependencia(paginada=True)
        self.params_excel = self._dependencia(paginada=False)

    def _dependencia(self, paginada: bool):
        """Dependencia de FastAPI con un query param por filtro, para que salgan en /docs."""
        parametros = []
        if paginada:
            parametros += [
                inspect.Parameter("page", inspect.Parameter.KEYWORD_ONLY, annotation=int, default=Query(1, ge=1)),
                inspect.Parameter("size", inspect.Parameter.KEYWORD_ONLY, annotation=int, default=Query(50, ge=1, le=self.max_size)),
            ]
        if self.ordenables:
            opciones = ", ".join(self.ordenables)
            parametros.append(inspect.Parameter(
                "orden", inspect.Parameter.KEYWORD_ONLY, annotation=Optional[str],
                default=Query(None, description=f"Campo de orden, con '-' para descendente: {opciones}"),
            ))
        for nombre, filtro in self.filtros.items():
            parametros.append(inspect.Parameter(
                nombre, inspect.Parameter.KEYWORD_ONLY, annotation=filtro.tipo_parametro(),
                default=Query(None, description=filtro.descripcion),
            ))

        def dependencia(**params):
            return params

        dependencia.__signature__ = inspect.Signature(parametros)
        return dependencia

    def query(self, db: Session, params: dict):
        """Query con los filtros aplicados, sin orden ni paginación."""
        query = db.query(self.pk.class_)
        for nombre, filtro in self.filtros.items():
            valor = params.get(nombre)
            if isinstance(valor, str):
                valor = valor.strip() or None  # texto vacío = sin filtro
            if valor is not None and valor != []:
                query = query.filter(_OPERADORES[filtro.operador](filtro.columna, valor))
        return query

    def con_relaciones(self, query, excel: bool = False):
        relaciones = self.relaciones + self.relaciones_excel if excel else self.relaciones
        return query.options(*(joinedload(r) for r in relaciones))

    def ordenar(self, query, params: dict):
        orden = params.get("orden")
        if not orden:
            return query.order_by(*self.orden)
        descendente = orden.startswith("-")
        columna = self.ordenables.get(orden.lstrip("-"))
        if columna is None:
            raise HTTPException(status_code=422, detail=f"No se puede ordenar por '{orden.lstrip('-')}'")
        # La PK desempata para que la paginación sea estable
        return query.order_by(columna.desc() if descendente else columna.asc(), self.pk.asc())


def paginar(db: Session, config: ListaConfig, params: dict) -> dict:
    query = config.query(db, params)
    total = query.with_entities(func.count(config.pk)).scalar()
    page, size = params["page"], params["size"]
    items = (
        config.ordenar(config.con_relaciones(query), params)
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )
    return {"total": total, "page": page, "size": size, "items": items}


def _valor_ruta(objeto, ruta: str):
    for parte in ruta.split("."):
        if objeto is None:
            return None
        objeto = getattr(objeto, parte)
    return objeto


def _celda_excel(hoja, valor):
    if isinstance(valor, bool):
        valor = "Sí" if valor else "No"
    elif isinstance(valor, Decimal):
        valor = float(valor)
    celda = WriteOnlyCell(hoja, value=valor)
    if isinstance(valor, str) and valor.startswith("="):
        celda.data_type = "s"  # texto que empieza por "=" no se debe evaluar como fórmula
    elif isinstance(valor, datetime):
        celda.number_format = "yyyy-mm-dd hh:mm"
    elif isinstance(valor, date):
        celda.number_format = "yyyy-mm-dd"
    return celda


def exportar_excel(db: Session, config: ListaConfig, params: dict, nombre: str) -> Response:
    query = config.query(db, params)
    total = query.with_entities(func.count(config.pk)).scalar()
    if total > config.max_filas_excel:
        raise HTTPException(
            status_code=400,
            detail=f"La exportación tiene {total} registros y el máximo es {config.max_filas_excel}. Aplica más filtros.",
        )

    libro = Workbook(write_only=True)
    hoja = libro.create_sheet(nombre[:31])
    hoja.freeze_panes = "A2"
    for indice, (titulo, _) in enumerate(config.columnas_excel, start=1):
        hoja.column_dimensions[get_column_letter(indice)].width = max(len(titulo) + 4, 14)

    negrita = Font(bold=True)
    encabezados = []
    for titulo, _ in config.columnas_excel:
        celda = WriteOnlyCell(hoja, value=titulo)
        celda.font = negrita
        encabezados.append(celda)
    hoja.append(encabezados)

    filas = config.ordenar(config.con_relaciones(query, excel=True), params).yield_per(1000)
    for fila in filas:
        hoja.append([_celda_excel(hoja, _valor_ruta(fila, ruta)) for _, ruta in config.columnas_excel])

    salida = BytesIO()
    libro.save(salida)
    archivo = f"{nombre}_{ahora_local():%Y-%m-%d}.xlsx"
    return Response(
        content=salida.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{archivo}"'},
    )
