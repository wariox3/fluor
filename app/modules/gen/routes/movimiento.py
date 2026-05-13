from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.core.config import DEFAULT_EMPRESA_ID
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.gen.models.movimiento import Movimiento
from app.modules.gen.models.movimiento_tipo import MovimientoTipo
from app.modules.gen.models.item import Item
from app.modules.gen.models.tercero import Tercero
from app.modules.gen.models.movimiento_detalle import MovimientoDetalle
from app.modules.gen.schemas.movimiento import MovimientoListResponse, MovimientoResponse, MovimientoCreate, MovimientoActualizarInterface

router = APIRouter()

@router.post("/nuevo-documento", response_model=MovimientoResponse)
def nuevo_documento(data: MovimientoCreate, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):

    movimiento_tipo = db.query(MovimientoTipo).filter(MovimientoTipo.codigo_movimiento_tipo_pk == data.codigo_movimiento_tipo_fk).first()
    if not movimiento_tipo:
        raise HTTPException(status_code=404, detail=f"MovimientoTipo '{data.codigo_movimiento_tipo_fk}' no existe")

    tercero = db.query(Tercero).filter(Tercero.codigo_tercero_pk == data.codigo_tercero_fk).first()
    if not tercero:
        raise HTTPException(status_code=404, detail=f"Tercero '{data.codigo_tercero_fk}' no existe")

    movimiento = Movimiento(
        fecha=data.fecha,
        fecha_vence=data.fecha_vence,
        codigo_tercero_fk=data.codigo_tercero_fk,
        codigo_forma_pago_fk=tercero.codigo_forma_pago_fk,
        codigo_centro_costo_fk=data.codigo_centro_costo_fk,
        codigo_movimiento_tipo_fk=data.codigo_movimiento_tipo_fk,
        codigo_resolucion_fk=data.codigo_resolucion_fk,
        codigo_movimiento_clase_fk=movimiento_tipo.codigo_movimiento_clase_fk,
        plazo_pago=data.plazo_pago,
        soporte=data.soporte,
        orden_compra=data.orden_compra,
        comentarios=data.comentarios,
        operacion_inventario=movimiento_tipo.operacion_inventario,
        operacion_comercial=movimiento_tipo.operacion_comercial,
        codigo_interface=data.codigo_interface,
        codigo_empresa_fk=DEFAULT_EMPRESA_ID,
    )
    db.add(movimiento)
    db.flush() 

    # Crear los detalles
    detalles_creados = []
    for detalle_data in data.detalles:

        item = db.query(Item).filter(Item.codigo_item_pk == detalle_data.codigo_item_fk).first()
        if not item:
            raise HTTPException(status_code=404, detail=f"Item '{detalle_data.codigo_item_fk}' no existe")

        cantidad = detalle_data.cantidad or 0.0
        operacion = movimiento.operacion_inventario or 0

        detalle = MovimientoDetalle(
            codigo_movimiento_fk=movimiento.codigo_movimiento_pk,
            codigo_empresa_fk=DEFAULT_EMPRESA_ID,
            codigo_item_fk=detalle_data.codigo_item_fk,
            codigo_impuesto_retencion_fk=item.codigo_impuesto_retencion_fk,
            codigo_impuesto_iva_fk=item.codigo_impuesto_iva_venta_fk,
            codigo_tercero_fk=detalle_data.codigo_tercero_fk,
            codigo_centro_costo_fk=detalle_data.codigo_centro_costo_fk,
            detalle=detalle_data.detalle,
            cantidad=cantidad,
            cantidad_operada=cantidad * operacion,
            cantidad_pendiente=cantidad,
            vr_precio=detalle_data.vr_precio,
            operacion_inventario=movimiento.operacion_inventario,
        )
        db.add(detalle)
        detalles_creados.append(detalle)

    db.commit()
    db.refresh(movimiento)

    movimiento.detalles = detalles_creados

    return movimiento

@router.get("/lista", response_model=MovimientoListResponse)
def lista(page: int = 1, size: int = 50, movimiento_id: Optional[int] = None, codigo_interface: Optional[str] = None, numero: Optional[int] = None, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    query = db.query(Movimiento)
    if movimiento_id:
        query = query.filter(Movimiento.codigo_movimiento_pk == movimiento_id)
    if codigo_interface:
        query = query.filter(Movimiento.codigo_interface == codigo_interface)
    if numero is not None:
        query = query.filter(Movimiento.numero == numero)
    total = query.with_entities(func.count(Movimiento.codigo_movimiento_pk)).scalar()
    offset = (page - 1) * size
    movimientos = query.offset(offset).limit(size).all()
    return MovimientoListResponse(total=total, page=page, size=size, items=movimientos)

@router.patch("/{movimiento_id}/actualizar-interface", response_model=MovimientoResponse)
def actualizar_interface(
    movimiento_id: int,
    payload: MovimientoActualizarInterface,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    
    movimiento = db.query(Movimiento).filter(
        Movimiento.codigo_movimiento_pk == movimiento_id
    ).first()

    if not movimiento:
        raise HTTPException(
            status_code=404,
            detail="Movimiento no encontrado"
        )

    if payload.codigo_interface is not None:
        movimiento.codigo_interface = payload.codigo_interface

    db.commit()
    db.refresh(movimiento)

    return movimiento