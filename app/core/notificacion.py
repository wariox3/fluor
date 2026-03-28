import asyncio
from typing import Dict
from sqlalchemy.orm import Session
from app.modules.auth.models.notificacion import Notificacion

# Colas SSE por usuario_id
_colas: Dict[int, asyncio.Queue] = {}


def registrar_cola(usuario_id: int) -> asyncio.Queue:
    cola = asyncio.Queue()
    _colas[usuario_id] = cola
    return cola


def eliminar_cola(usuario_id: int):
    _colas.pop(usuario_id, None)


def crear_notificacion(
    db: Session,
    usuario_id: int,
    tipo: str,
    titulo: str,
    mensaje: str = None,
    url: str = None,
) -> Notificacion:
    notif = Notificacion(
        usuario_id=usuario_id,
        tipo=tipo,
        titulo=titulo,
        mensaje=mensaje,
        url=url,
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)

    # Empujar al stream SSE si el usuario está conectado
    cola = _colas.get(usuario_id)
    if cola:
        try:
            cola.put_nowait({
                "id": notif.id,
                "tipo": notif.tipo,
                "titulo": notif.titulo,
                "mensaje": notif.mensaje,
                "url": notif.url,
                "fecha_creacion": notif.fecha_creacion.isoformat(),
            })
        except asyncio.QueueFull:
            pass

    return notif
