import asyncio
import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.master_database import get_master_db
from app.core.security import get_current_user, require_admin
from app.core.notificacion import registrar_cola, eliminar_cola, crear_notificacion
from app.modules.auth.models.notificacion import Notificacion
from app.modules.auth.schemas.notificacion import (
    NotificacionCreate,
    NotificacionListResponse,
    NotificacionResponse,
    ContadorResponse,
)

router = APIRouter()


@router.post("/crear", response_model=NotificacionResponse)
def crear(
    data: NotificacionCreate,
    db: Session = Depends(get_master_db),
    _: dict = Depends(require_admin),
):
    notif = crear_notificacion(
        db,
        usuario_id=data.usuario_id,
        tipo=data.tipo,
        titulo=data.titulo,
        mensaje=data.mensaje,
        url=data.url,
    )
    return notif


@router.get("/stream")
async def stream(current_user: dict = Depends(get_current_user)):
    usuario_id = int(current_user["sub"])
    cola = registrar_cola(usuario_id)

    async def generador():
        try:
            # Evento de conexión
            yield "event: conectado\ndata: {}\n\n"
            while True:
                try:
                    datos = await asyncio.wait_for(cola.get(), timeout=30)
                    yield f"event: notificacion\ndata: {json.dumps(datos)}\n\n"
                except asyncio.TimeoutError:
                    yield ": ping\n\n"
        finally:
            eliminar_cola(usuario_id)

    return StreamingResponse(
        generador(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/lista", response_model=NotificacionListResponse)
def lista(
    page: int = 1,
    size: int = 20,
    solo_no_leidas: bool = False,
    db: Session = Depends(get_master_db),
    current_user: dict = Depends(get_current_user),
):
    usuario_id = int(current_user["sub"])
    query = db.query(Notificacion).filter(Notificacion.usuario_id == usuario_id)
    if solo_no_leidas:
        query = query.filter(Notificacion.leida == False)
    total = query.with_entities(func.count(Notificacion.id)).scalar()
    offset = (page - 1) * size
    items = query.order_by(Notificacion.fecha_creacion.desc()).offset(offset).limit(size).all()
    return NotificacionListResponse(total=total, page=page, size=size, items=items)


@router.get("/contador", response_model=ContadorResponse)
def contador(
    db: Session = Depends(get_master_db),
    current_user: dict = Depends(get_current_user),
):
    usuario_id = int(current_user["sub"])
    no_leidas = (
        db.query(func.count(Notificacion.id))
        .filter(Notificacion.usuario_id == usuario_id, Notificacion.leida == False)
        .scalar()
    )
    return ContadorResponse(no_leidas=no_leidas)


@router.patch("/{notificacion_id}/leer", response_model=NotificacionResponse)
def leer(
    notificacion_id: int,
    db: Session = Depends(get_master_db),
    current_user: dict = Depends(get_current_user),
):
    usuario_id = int(current_user["sub"])
    notif = db.query(Notificacion).filter(
        Notificacion.id == notificacion_id,
        Notificacion.usuario_id == usuario_id,
    ).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    notif.leida = True
    db.commit()
    db.refresh(notif)
    return notif


@router.patch("/leer-todas")
def leer_todas(
    db: Session = Depends(get_master_db),
    current_user: dict = Depends(get_current_user),
):
    usuario_id = int(current_user["sub"])
    db.query(Notificacion).filter(
        Notificacion.usuario_id == usuario_id,
        Notificacion.leida == False,
    ).update({"leida": True})
    db.commit()
    return {"detail": "Todas las notificaciones marcadas como leídas"}
