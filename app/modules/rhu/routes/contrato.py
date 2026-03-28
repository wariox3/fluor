from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session, joinedload
from typing import Optional
from sqlalchemy import func
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.rhu.models.contrato import Contrato
from app.modules.rhu.models.empleado import Empleado
from app.modules.rhu.schemas.contrato import ContratoListResponse
from app.core.pdf_template import generar_pdf
from app.core.utils import fecha_larga, fmt_numero
from app.modules.gen.models.configuracion import Configuracion
from app.modules.gen.models.formato import Formato

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


@router.get("/imprimir-certificado-laboral")
def imprimir_certificado_laboral(contrato_id: int, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    contrato = (
        db.query(Contrato)
        .options(
            joinedload(Contrato.cargo_rel),
            joinedload(Contrato.contrato_tipo_rel),
            joinedload(Contrato.empleado_rel),
        )
        .filter(Contrato.codigo_contrato_pk == contrato_id)
        .first()
    )
    if not contrato:
        raise HTTPException(status_code=404, detail="No se encontró contrato")

    config = (
        db.query(Configuracion)
        .options(joinedload(Configuracion.ciudad_rel))
        .first()
    )
    
    if(contrato.estado_terminado == False):
        formato = db.query(Formato).filter(Formato.codigo_formato_pk == 13).first()
    else:
        formato = db.query(Formato).filter(Formato.codigo_formato_pk == 12).first()

    nit_raw             = getattr(config, "nit", "") if config else ""
    dv                  = getattr(config, "digito_verificacion", "") if config else ""
    ciudad_rel          = getattr(config, "ciudad_rel", None) if config else None
    empleado_rel        = getattr(contrato, "empleado_rel", None)
    cargo_rel           = getattr(contrato, "cargo_rel", None)
    contrato_tipo_rel   = getattr(contrato, "contrato_tipo_rel", None)

    etiquetas = {
        "FECHA_HOY":                        fecha_larga(date.today()),
        "EMPRESA_NOMBRE":                   empleado_rel.nombre_corto.upper() if empleado_rel else "",
        "EMPRESA_IDENTIFICACION":           empleado_rel.numero_identificacion.upper() if empleado_rel else "",
        "EMPRESA_NOMBRE":                   getattr(config, "nombre", "").upper() if config else "",
        "EMPRESA_IDENTIFICACION_COMPLETO":  f"{nit_raw}-{dv}",
        "EMPRESA_CIUDAD":                   ciudad_rel.nombre if ciudad_rel else "",
        "FECHA_INGRESO":                    fecha_larga(contrato.fecha_desde) if contrato.fecha_desde else "",
        "FECHA_TERMINO":                    fecha_larga(contrato.fecha_hasta) if contrato.fecha_hasta else "",
        "TIPO_CONTRATO":                    contrato_tipo_rel.nombre.upper() if contrato_tipo_rel else "",
        "CARGO":                            cargo_rel.nombre.upper() if cargo_rel else "",
        "SALARIO":                          fmt_numero(getattr(contrato, "vr_salario", 0)),                
        "TELEFONO":                         getattr(config, "telefono",  "") if config else "",
        "EMAIL":                            getattr(config, "correo",    "") if config else "",
        "DIRECCION":                        getattr(config, "direccion", "") if config else "",
    }

    pdf_bytes = generar_pdf(etiquetas, formato)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=certificado_{contrato_id}.pdf"},
    )
