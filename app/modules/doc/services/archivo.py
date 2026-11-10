"""
Consulta y descarga de los archivos documentales heredados de holmio (`doc_archivo`).

Holmio registra cada archivo con el modelo dueño (`codigo_archivo_tipo_fk`, p. ej. `CrmVisita`)
y el id del registro dueño (`codigo`), y guarda el contenido en Backblaze.
"""

from urllib.parse import quote

import httpx
from fastapi import HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Query, Session

from app.core.backblaze import b2_client
from app.modules.doc.models.archivo import Archivo
from app.modules.gen.models.configuracion import Configuracion


def query_archivos(db: Session, codigo_modelo: str, codigo: int, solo_portal: bool = False) -> Query:
    """
    Archivos de un registro de holmio. Con `solo_portal`, solo los que la empresa marcó en
    holmio para el portal de clientes (`portal_clientes`).
    """
    query = db.query(Archivo).filter(
        Archivo.codigo_archivo_tipo_fk == codigo_modelo,
        Archivo.codigo == str(codigo),
    )
    if solo_portal:
        query = query.filter(Archivo.portal_clientes.is_(True))
    return query


def descargar(db: Session, archivo: Archivo) -> Response:
    """
    Descarga el archivo desde Backblaze, en la misma ruta que usa holmio:
    `{ruta_almacenamiento_servicio}/archivo/{codigo_archivo_pk}.{extension_original}`.
    """
    configuracion = db.query(Configuracion).first()
    ruta_base = configuracion.ruta_almacenamiento_servicio if configuracion else None
    if not ruta_base:
        raise HTTPException(status_code=409, detail="La empresa no tiene configurado el almacenamiento de archivos")
    ruta = f"{ruta_base}/archivo/{archivo.codigo_archivo_pk}.{archivo.extension_original}"

    try:
        contenido, content_type = b2_client.download_file(ruta)
    except httpx.HTTPStatusError as error:
        if error.response.status_code == 404:
            raise HTTPException(status_code=404, detail="El archivo no está en el almacenamiento") from error
        raise HTTPException(status_code=502, detail="Error al descargar el archivo desde el almacenamiento") from error
    except httpx.HTTPError as error:
        raise HTTPException(status_code=502, detail="Error al descargar el archivo desde el almacenamiento") from error

    # En holmio `nombre` ya trae la extensión: es el nombre original del archivo cargado
    nombre = archivo.nombre or f"{archivo.codigo_archivo_pk}.{archivo.extension_original}"
    return Response(
        content=contenido,
        media_type=archivo.tipo or content_type,
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{quote(nombre)}"},
    )
