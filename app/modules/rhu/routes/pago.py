from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
from sqlalchemy import func
from io import BytesIO
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.rhu.formats import pago_pdf
from app.modules.rhu.models.pago import Pago
from app.modules.rhu.models.empleado import Empleado
from app.modules.rhu.schemas.pago import PagoListResponse
from app.modules.rhu.formats import pago_pdf

router = APIRouter()


@router.get("/lista", response_model=PagoListResponse)
def lista(page: int = 1, size: int = 50, empleado_id: Optional[int] = None, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    query = db.query(Pago)
    if empleado_id:
        query = query.filter(Pago.codigo_empleado_fk == empleado_id)
    total = query.with_entities(func.count(Pago.codigo_pago_pk)).scalar()
    offset = (page - 1) * size
    pagos = query.offset(offset).limit(size).all()
    return PagoListResponse(total=total, page=page, size=size, items=pagos)


@router.get("/pdf")
def lista_pdf(empleado_id: Optional[int] = None, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user),):
    query = db.query(Pago)
    if empleado_id:
        query = query.filter(Pago.codigo_empleado_fk == empleado_id)
    pagos = query.order_by(Pago.fecha_desde.desc()).all()

    pdf_bytes = pago_pdf.generar(pagos, empleado_id)

    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": "inline; filename=pagos.pdf"},
    )


@router.get("/{pago_id}/imprimir")
def imprimir(pago_id: int, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    pago = db.query(Pago).filter(Pago.codigo_pago_pk == pago_id).first()
    if not pago:
        raise HTTPException(status_code=404, detail="Pago no encontrado")
    empleado = db.query(Empleado).filter(Empleado.codigo_empleado_pk == pago.codigo_empleado_fk).first()
    pdf_bytes = pago_pdf.generar(pago, empleado)
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=pago_{pago_id}.pdf"},
    )