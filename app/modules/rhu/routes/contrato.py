from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import func
from datetime import date
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.rhu.models.contrato import Contrato
from app.modules.rhu.models.empleado import Empleado
from app.modules.rhu.schemas.contrato import ContratoListResponse
from app.modules.rhu.formats.certificado_laboral_pdf import generar as generar_certificado
from app.modules.gen.models.configuracion import Configuracion
from app.modules.gen.models.imagen import Imagen

router = APIRouter()


@router.get("/lista", response_model=ContratoListResponse)
def lista(page: int = 1, size: int = 50, empleado_id: Optional[int] = None, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    query = db.query(Contrato)
    if empleado_id:
        query = query.filter(Contrato.codigo_empleado_fk == empleado_id)
    total = query.with_entities(func.count(Contrato.codigo_contrato_pk)).scalar()
    offset = (page - 1) * size
    contratos = query.offset(offset).limit(size).all()
    return ContratoListResponse(total=total, page=page, size=size, items=contratos)


@router.get("/imprimir-certificado-activo")
def imprimir_certificado_activo(contrato_id: int, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user),):
    contrato = (
        db.query(Contrato)
        .filter(
            Contrato.codigo_contrato_pk == contrato_id
        )
        .first()
    )

    if not contrato:
        raise HTTPException(status_code=404, detail="No se encontró contrato activo")

    empleado = db.query(Empleado).filter(Empleado.codigo_empleado_pk == contrato.codigo_empleado_fk).first()
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    config = db.query(Configuracion).with_entities(
        Configuracion.nombre,
        Configuracion.nit,
        Configuracion.digito_verificacion,
        Configuracion.telefono,
        Configuracion.direccion,
        Configuracion.correo,
    ).first()
    gen_imagen = db.query(Imagen).filter(Imagen.codigo_imagen_pk == "LOGO").first()
    pdf_bytes = generar_certificado(empleado, contrato, config, gen_imagen)

    nombre_archivo = f"certificado_laboral_{contrato_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename={nombre_archivo}"},
    )