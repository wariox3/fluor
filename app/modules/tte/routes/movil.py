from typing import Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from app.core.master_database import get_master_db
from app.core.security import get_current_user_from_token
from app.core.tenant_database import DespachoContexto, get_despacho_db
from app.core.utils import a_hora_local, ahora_local
from app.modules.tte.models.ciudad import Ciudad
from app.modules.tte.models.despacho import Despacho
from app.modules.tte.models.despacho_detalle import DespachoDetalle
from app.modules.tte.models.guia import Guia
from app.modules.tte.models.ubicacion import Ubicacion
from app.modules.tte.schemas.guia import GuiaEntregaResponse
from app.modules.tte.schemas.movil import (
    MovilDespachoGuiasResponse,
    MovilGuiaResponse,
    MovilUbicacionLoteRequest,
    MovilUbicacionLoteResponse,
    MovilUbicacionRequest,
    MovilUbicacionResponse,
)
from app.modules.tte.services import guia as guia_service

router = APIRouter()


@router.get("/guias", response_model=MovilDespachoGuiasResponse)
def despacho_guias(contexto: DespachoContexto = Depends(get_despacho_db)):
    """Todas las guías del despacho asignado, para guardarlas en el teléfono y trabajar sin señal."""
    db = contexto.db
    despacho = db.query(Despacho).filter(Despacho.codigo_despacho_pk == contexto.codigo_despacho).first()
    if not despacho or despacho.estado_anulado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Despacho no encontrado")

    # Las guías del despacho están en tte_despacho_detalle; unidades y valores son los de este despacho
    filas = (
        db.query(DespachoDetalle, Guia, Ciudad.nombre)
        .join(Guia, Guia.codigo_guia_pk == DespachoDetalle.codigo_guia_fk)
        .outerjoin(Ciudad, Ciudad.codigo_ciudad_pk == Guia.codigo_ciudad_destino_fk)
        .filter(DespachoDetalle.codigo_despacho_fk == contexto.codigo_despacho, Guia.estado_anulado == False)
        .order_by(Guia.orden_ruta, DespachoDetalle.codigo_despacho_detalle_pk)
        .all()
    )
    guias = [
        MovilGuiaResponse(
            codigo_despacho_detalle=detalle.codigo_despacho_detalle_pk,
            codigo_guia=guia.codigo_guia_pk,
            documento_cliente=guia.documento_cliente,
            nombre_remitente=guia.nombre_remitente,
            nombre_destinatario=guia.nombre_destinatario,
            direccion_destinatario=guia.direccion_destinatario,
            telefono_destinatario=guia.telefono_destinatario,
            ciudad_destino=ciudad_destino,
            unidades=detalle.unidades or 0,
            peso_real=detalle.peso_real or 0,
            vr_recaudo=detalle.vr_recaudo or 0,
            vr_cobro_entrega=detalle.vr_cobro_entrega or 0,
            orden_ruta=guia.orden_ruta,
            latitud=guia.latitud,
            longitud=guia.longitud,
            requiere_cita=bool(guia.requiere_cita),
            comentario=guia.comentario,
            estado_entregado=bool(guia.estado_entregado),
            estado_novedad=bool(guia.estado_novedad),
            fecha_entrega=guia.fecha_entrega,
        )
        for detalle, guia, ciudad_destino in filas
    ]
    return MovilDespachoGuiasResponse(
        tenant_despacho_id=contexto.tenant_despacho_id,
        tenant_id=contexto.tenant_id,
        tenant_nombre=contexto.tenant_nombre,
        codigo_despacho=contexto.codigo_despacho,
        numero=despacho.numero,
        fecha_salida=despacho.fecha_salida,
        total=len(guias),
        guias=guias,
    )


@router.post("/guia/entrega", response_model=GuiaEntregaResponse)
def guia_entrega(
    datos: str = Form(..., description="JSON con los datos de la entrega (GuiaEntregaRequest); se ignora `usuario`"),
    imagenes: list[UploadFile] = File(default=[], description="Fotos de la entrega, JPEG, PNG o WebP"),
    firma: Optional[UploadFile] = File(default=None, description="Firma de quien recibe, PNG"),
    contexto: DespachoContexto = Depends(get_despacho_db),
    master_db: Session = Depends(get_master_db),
    current_user: dict = Depends(get_current_user_from_token),
):
    """Entrega de una guía del despacho asignado al repartidor.
    Solo guías de ese despacho; el usuario de la entrega es siempre el autenticado."""
    db = contexto.db
    payload = guia_service.parsear_datos_entrega(datos)

    despacho = db.query(Despacho).filter(Despacho.codigo_despacho_pk == contexto.codigo_despacho).first()
    if not despacho or despacho.estado_anulado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Despacho no encontrado")
    if despacho.estado_cerrado:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El despacho está cerrado")

    # Misma fuente que la lista de guías del despacho; la guía anulada la rechaza registrar_entrega
    en_despacho = (
        db.query(DespachoDetalle.codigo_despacho_detalle_pk)
        .filter(
            DespachoDetalle.codigo_despacho_fk == contexto.codigo_despacho,
            DespachoDetalle.codigo_guia_fk == payload.guia,
        )
        .first()
    )
    if not en_despacho:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guía no encontrada")

    archivos_imagenes, archivo_firma = guia_service.leer_archivos_entrega(imagenes, firma)
    usuario = guia_service.usuario_autenticado(master_db, current_user)
    return guia_service.registrar_entrega(db, payload, archivos_imagenes, archivo_firma, usuario)


@router.post("/despacho/ubicacion", response_model=MovilUbicacionResponse)
def despacho_ubicacion(
    payload: MovilUbicacionRequest,
    contexto: DespachoContexto = Depends(get_despacho_db),
    master_db: Session = Depends(get_master_db),
    current_user: dict = Depends(get_current_user_from_token),
):
    """Registra la ubicación actual del repartidor en el despacho asignado
    y la deja como última ubicación del despacho."""
    db = contexto.db
    despacho = db.query(Despacho).filter(Despacho.codigo_despacho_pk == contexto.codigo_despacho).first()
    if not despacho or despacho.estado_anulado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Despacho no encontrado")
    if despacho.estado_cerrado:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El despacho está cerrado")

    ahora = ahora_local()
    ubicacion = Ubicacion(
        codigo_despacho_fk=despacho.codigo_despacho_pk,
        fecha=ahora,
        usuario=guia_service.usuario_autenticado(master_db, current_user),
        latitud=payload.latitud,
        longitud=payload.longitud,
        velocidad=payload.velocidad or 0,
        altitud=payload.altitud or 0,
        exactitud=payload.exactitud or 0,
        exactitud_altitud=payload.exactitud_altitud or 0,
    )
    db.add(ubicacion)
    despacho.ultima_latitud = payload.latitud
    despacho.ultima_longitud = payload.longitud
    despacho.fecha_ultimo_reporte = ahora
    db.commit()
    db.refresh(ubicacion)
    return MovilUbicacionResponse(
        codigo_ubicacion=ubicacion.codigo_ubicacion_pk,
        codigo_despacho=despacho.codigo_despacho_pk,
        fecha=ubicacion.fecha,
        latitud=ubicacion.latitud,
        longitud=ubicacion.longitud,
    )


@router.post("/despacho/ubicacion-lote", response_model=MovilUbicacionLoteResponse)
def despacho_ubicacion_lote(
    payload: MovilUbicacionLoteRequest,
    contexto: DespachoContexto = Depends(get_despacho_db),
    master_db: Session = Depends(get_master_db),
    current_user: dict = Depends(get_current_user_from_token),
):
    """Registra varias ubicaciones capturadas en el teléfono (p. ej. sin señal) con su fecha de captura.
    Es idempotente: un punto con la misma fecha (al segundo) que uno ya guardado del despacho se omite.
    La última ubicación del despacho solo se actualiza si el lote trae un punto más reciente."""
    db = contexto.db
    despacho = db.query(Despacho).filter(Despacho.codigo_despacho_pk == contexto.codigo_despacho).first()
    if not despacho or despacho.estado_anulado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Despacho no encontrado")
    if despacho.estado_cerrado:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El despacho está cerrado")

    ahora = ahora_local()
    # Fecha del teléfono en hora del negocio; sin segundos fraccionarios porque DateTime de MySQL los descarta.
    # Una fecha futura (reloj del teléfono adelantado) se recorta a la hora del servidor.
    puntos = [
        (min(a_hora_local(item.fecha).replace(microsecond=0), ahora), item)
        for item in payload.ubicaciones
    ]
    puntos.sort(key=lambda p: p[0])

    # Dedupe por fecha (al segundo): latitud/longitud son FLOAT simple en MySQL y no vuelven idénticas
    existentes = {
        fecha
        for (fecha,) in db.query(Ubicacion.fecha).filter(
            Ubicacion.codigo_despacho_fk == despacho.codigo_despacho_pk,
            Ubicacion.fecha >= puntos[0][0],
            Ubicacion.fecha <= puntos[-1][0],
        )
    }

    usuario = guia_service.usuario_autenticado(master_db, current_user)
    nuevas = []
    for fecha, item in puntos:
        if fecha in existentes:
            continue
        existentes.add(fecha)
        nuevas.append(
            Ubicacion(
                codigo_despacho_fk=despacho.codigo_despacho_pk,
                fecha=fecha,
                usuario=usuario,
                latitud=item.latitud,
                longitud=item.longitud,
                velocidad=item.velocidad or 0,
                altitud=item.altitud or 0,
                exactitud=item.exactitud or 0,
                exactitud_altitud=item.exactitud_altitud or 0,
            )
        )
    db.add_all(nuevas)

    ultima_fecha, ultimo = puntos[-1]
    if despacho.fecha_ultimo_reporte is None or ultima_fecha >= despacho.fecha_ultimo_reporte:
        despacho.ultima_latitud = ultimo.latitud
        despacho.ultima_longitud = ultimo.longitud
        despacho.fecha_ultimo_reporte = ultima_fecha
    db.commit()

    return MovilUbicacionLoteResponse(
        codigo_despacho=despacho.codigo_despacho_pk,
        recibidas=len(puntos),
        registradas=len(nuevas),
        duplicadas=len(puntos) - len(nuevas),
        fecha_ultimo_reporte=despacho.fecha_ultimo_reporte,
    )
