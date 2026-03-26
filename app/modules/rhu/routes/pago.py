from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from typing import Optional
from sqlalchemy import func
from io import BytesIO
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.rhu.formats import pago_pdf
from app.modules.rhu.models.pago import Pago
from app.modules.rhu.models.pago_tipo import PagoTipo
from app.modules.rhu.models.pago_detalle import PagoDetalle
from app.modules.rhu.models.contrato import Contrato
from app.modules.rhu.models.empleado import Empleado
from app.modules.tur.models.programacion_respaldo import ProgramacionRespaldo
from app.modules.rhu.schemas.pago import PagoListResponse

router = APIRouter()


@router.get("/lista", response_model=PagoListResponse)
def lista(page: int = 1, size: int = 50, empleado_id: Optional[int] = None, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    query = (
        db.query(Pago)
        .join(PagoTipo, Pago.codigo_pago_tipo_fk == PagoTipo.codigo_pago_tipo_pk)
        .options(joinedload(Pago.pago_tipo))
        .filter(
            PagoTipo.habilitado_portal == True,
            Pago.estado_autorizado == True,
            Pago.estado_aprobado == True,
            Pago.habilitado_portal == True,
            Pago.estado_anulado == False,
        )
    )
    if empleado_id:
        query = query.filter(Pago.codigo_empleado_fk == empleado_id)
    total = query.with_entities(func.count(Pago.codigo_pago_pk)).scalar()
    offset = (page - 1) * size
    pagos = query.offset(offset).limit(size).all()
    return PagoListResponse(total=total, page=page, size=size, items=pagos)


@router.get("/{pago_id}/imprimir")
def imprimir(pago_id: int, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    pago = (
        db.query(Pago)
        .options(
            joinedload(Pago.empleado).joinedload(Empleado.banco_rel),
            joinedload(Pago.empleado).joinedload(Empleado.zona_rel),
            joinedload(Pago.pago_tipo),
            joinedload(Pago.periodo_rel),
            joinedload(Pago.cargo_rel),
            joinedload(Pago.entidad_pension_rel),
            joinedload(Pago.entidad_salud_rel),
            joinedload(Pago.contrato_rel).joinedload(Contrato.grupo_rel),
            joinedload(Pago.contrato_rel).joinedload(Contrato.puesto_rel),
            joinedload(Pago.contrato_rel).joinedload(Contrato.tercero_rel),
        )
        .filter(Pago.codigo_pago_pk == pago_id)
        .first()
    )
    if not pago:
        raise HTTPException(status_code=404, detail="Pago no encontrado")
    detalles = (
        db.query(PagoDetalle)
        .options(joinedload(PagoDetalle.concepto))
        .filter(PagoDetalle.codigo_pago_fk == pago_id)
        .order_by(PagoDetalle.codigo_concepto_fk)
        .all()
    )
    programacion = []
    if pago.codigo_soporte_contrato_fk:
        programacion = (
            db.query(ProgramacionRespaldo)
            .filter(ProgramacionRespaldo.codigo_soporte_contrato_fk == pago.codigo_soporte_contrato_fk)
            .all()
        )
    pdf_bytes = pago_pdf.generar(pago, detalles, db, programacion)
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=pago_{pago_id}.pdf"},
    )
