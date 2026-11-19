import json

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.utils import a_hora_local, ahora_local
from app.modules.tte.models.guia import Guia
from app.modules.tte.models.novedad import Novedad
from app.modules.tte.models.novedad_tipo import NovedadTipo
from app.modules.tte.models.seguimiento import Seguimiento
from app.modules.tte.schemas.novedad import NovedadCreateRequest, NovedadCreateResponse
from app.modules.tte.services import guia as guia_service


def registrar_novedad(db: Session, payload: NovedadCreateRequest, archivos_imagenes: list[bytes],
                      usuario: str, solo_movil: bool = False) -> NovedadCreateResponse:
    """Crea la novedad, marca la guía con novedad, registra el seguimiento NOVEDAD y sube las fotos.
    Las imágenes ya deben venir validadas (leer_archivos_entrega); `usuario` es quien la registra.
    Con solo_movil el tipo de novedad debe tener aplica_movil."""
    directorio_base = guia_service.directorio_documental(db) if archivos_imagenes else None

    # Se bloquea la fila para que dos novedades simultáneas no pasen ambas la validación de abierta
    guia = db.query(Guia).filter(Guia.codigo_guia_pk == payload.codigo_guia_fk).with_for_update().first()
    if not guia:
        raise HTTPException(status_code=404, detail="Guía no encontrada")
    if guia.estado_anulado:
        raise HTTPException(status_code=409, detail="La guía está anulada")
    if guia.estado_novedad and not guia.estado_novedad_solucion:
        raise HTTPException(status_code=409, detail="La guía ya tiene una novedad abierta")

    tipo = db.query(NovedadTipo).filter(NovedadTipo.codigo_novedad_tipo_pk == payload.codigo_novedad_tipo_fk).first()
    if not tipo:
        raise HTTPException(status_code=404, detail="Tipo de novedad no encontrado")
    if solo_movil and not tipo.aplica_movil:
        raise HTTPException(status_code=400, detail="El tipo de novedad no aplica para la aplicación móvil")

    ahora = ahora_local()
    fecha = a_hora_local(payload.fecha) if payload.fecha else ahora
    novedad = Novedad(
        codigo_novedad_tipo_fk=tipo.codigo_novedad_tipo_pk,
        codigo_guia_fk=guia.codigo_guia_pk,
        codigo_despacho_fk=guia.codigo_despacho_fk,
        descripcion=payload.descripcion,
        fecha=fecha,
        fecha_registro=ahora,
        fecha_reporte=ahora,
        usuario=usuario[:25],
        ingreso_api=True,
    )
    db.add(novedad)

    guia.estado_novedad = True
    guia.estado_novedad_solucion = False

    # Llave en camelCase: los clientes que consumen el seguimiento por interfaz la leen así
    datos = {"codigoNovedad": tipo.codigo_interface} if tipo.codigo_interface else None
    db.add(Seguimiento(
        codigo_guia_fk=guia.codigo_guia_pk,
        codigo_seguimiento_tipo_fk="NOVEDAD",
        fecha=ahora,
        fecha_seguimiento=fecha,
        usuario=usuario[:50],
        comentario=(tipo.nombre or tipo.codigo_novedad_tipo_pk)[:300],
        datos=json.dumps(datos) if datos else None,
        latitud=payload.latitud or 0,
        longitud=payload.longitud or 0,
    ))

    db.commit()
    db.refresh(novedad)

    # Las fotos se suben después de confirmar la novedad; si fallan, la novedad se mantiene
    errores = 0
    for data in archivos_imagenes:
        data, mime, extension, comprimido = guia_service.preparar_imagen(data, f"la novedad {novedad.codigo_novedad_pk}")
        if not guia_service.subir_fichero(db, "TteNovedad", novedad.codigo_novedad_pk, data,
                                          f"{novedad.codigo_novedad_pk}.{extension}", extension, mime,
                                          directorio_base, "fichero", usuario, comprimido=comprimido):
            errores += 1

    db.refresh(novedad)
    return NovedadCreateResponse.model_validate(novedad).model_copy(update={"ficheros_con_error": errores})
