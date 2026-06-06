from datetime import date
from logging import config
from app.modules.rhu.schemas import contrato
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session, joinedload
from typing import Optional
from sqlalchemy import func
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.rhu.models.contrato import Contrato
from app.modules.rhu.schemas.contrato import ContratoListResponse, ContratoResponse
from app.core.pdf_template import generar_pdf
from app.core.utils import fecha_larga, fmt_numero
from app.modules.gen.models.configuracion import Configuracion
from app.modules.gen.models.formato import Formato
from app.modules.gen.models.formato_imagen import FormatoImagen
from app.modules.rhu.routes.pago import salario_promedio_ultimos_pagos

router = APIRouter()

@router.get("/lista", response_model=ContratoListResponse)
def lista(page: int = 1, size: int = 50, empleado_id: Optional[int] = None, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    query = db.query(Contrato)
    if empleado_id:
        query = query.filter(Contrato.codigo_empleado_fk == empleado_id)
    total = query.with_entities(func.count(Contrato.codigo_contrato_pk)).scalar()
    offset = (page - 1) * size
    contratos = (
        query
        .options(
            joinedload(Contrato.contrato_tipo_rel),
            joinedload(Contrato.cargo_rel),
            joinedload(Contrato.grupo_rel),
        )
        .offset(offset)
        .limit(size)
        .all()
    )
    items = []
    for c in contratos:
        items.append(ContratoResponse(
            codigo_contrato_pk=c.codigo_contrato_pk,
            codigo_empleado_fk=c.codigo_empleado_fk,
            fecha_desde=c.fecha_desde,
            fecha_hasta=c.fecha_hasta,
            vr_salario=c.vr_salario,
            contrato_tipo_nombre=c.contrato_tipo_rel.nombre if c.contrato_tipo_rel else None,
            cargo_nombre=c.cargo_rel.nombre if c.cargo_rel else None,
            grupo_nombre=c.grupo_rel.nombre if c.grupo_rel else None,
        ))
    return ContratoListResponse(total=total, page=page, size=size, items=items)


@router.get("/imprimir-certificado-laboral")
def imprimir_certificado_laboral(contrato_id: int, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    contrato = (
        db.query(Contrato)
        .options(
            joinedload(Contrato.cargo_rel),
            joinedload(Contrato.contrato_tipo_rel),
            joinedload(Contrato.empleado_rel),
            joinedload(Contrato.entidad_salud_rel),
            joinedload(Contrato.entidad_pension_rel),
            joinedload(Contrato.ciudad_contrato_rel),
        )
        .filter(Contrato.codigo_contrato_pk == contrato_id)
        .first()
    )
    if not contrato:
        raise HTTPException(status_code=404, detail="No se encontró contrato")
    
    salario_promedio = salario_promedio_ultimos_pagos(
        db,
        contrato.codigo_contrato_pk,
        2
    )    

    config = (
        db.query(Configuracion)
        .options(joinedload(Configuracion.ciudad_rel))
        .first()
    )
    
    if(not contrato.estado_terminado):
        formato = db.query(Formato).filter(Formato.codigo_formato_pk == 13).first()
    else:
        formato = db.query(Formato).filter(Formato.codigo_formato_pk == 12).first()

    imagenes = []
    if formato:
        imagenes = db.query(FormatoImagen).filter(
            FormatoImagen.codigo_formato_fk == formato.codigo_formato_pk
        ).all()

    nit                 = getattr(config,       "nit", "") if config else ""
    dv                  = getattr(config,       "digito_verificacion", "") if config else ""
    ciudad_rel          = getattr(config,       "ciudad_rel", None) if config else None
    ciudad_contrato_rel = getattr(contrato,       "ciudad_contrato_rel", None) if config else None
    empleado_rel        = getattr(contrato,     "empleado_rel", None)
    cargo_rel           = getattr(contrato,     "cargo_rel", None)
    contrato_tipo_rel   = getattr(contrato,     "contrato_tipo_rel", None)
    entidad_salud_rel   = getattr(contrato,     "entidad_salud_rel", None)
    entidad_pension_rel = getattr(contrato,     "entidad_pension_rel", None)
    vr_auxilio_transporte = (getattr(config, "vr_auxilio_transporte", 0)
        if config and contrato.auxilio_transporte
        else 0
    )

    etiquetas = {
        "FECHA_HOY":                    fecha_larga(date.today()),
        "EMPRESA_NOMBRE":               getattr(config,   "nombre", "").upper() if config else "",
        "EMPRESA_IDENTIFICACION":       f"{nit}-{dv}",
        "EMPRESA_TELEFONO":             getattr(config, "telefono",  "") if config else "",
        "EMPRESA_EMAIL":                getattr(config, "correo",    "") if config else "",
        "EMPRESA_ DIRECCION":           getattr(config, "direccion", "") if config else "",
        "EMPRESA_CIUDAD":               ciudad_rel.nombre if ciudad_rel else "",                
        "EMPLEADO_NOMBRE":              empleado_rel.nombre_corto.upper() if empleado_rel else "",
        "EMPLEADO_IDENTIFICACION":      empleado_rel.numero_identificacion.upper() if empleado_rel else "",
        "FECHA_INGRESO":                fecha_larga(contrato.fecha_desde) if contrato.fecha_desde else "",
        "FECHA_TERMINO":                fecha_larga(contrato.fecha_hasta) if contrato.fecha_hasta else "",
        "TIPO_CONTRATO":                contrato_tipo_rel.nombre.upper() if contrato_tipo_rel else "",
        "CARGO":                        cargo_rel.nombre.upper() if cargo_rel else "",
        "SALARIO":                      fmt_numero(getattr(contrato, "vr_salario", 0)),
        "SALARIO_PROMEDIO_ULTIMOS_DOS_PAGOS": fmt_numero(salario_promedio),
        "ENTIDAD_SALUD":                entidad_salud_rel.nombre if entidad_salud_rel else "",
        "ENTIDAD_PENSION":              entidad_pension_rel.nombre if entidad_pension_rel else "",
        "CIUDAD_CONTRATACION":          ciudad_contrato_rel.nombre if ciudad_contrato_rel else "",
        "AUXILIO_TRANSPORTE":           fmt_numero(vr_auxilio_transporte),
        "ADICIONAL_CONTRATO":           fmt_numero(contrato.vr_adicional) if contrato.vr_adicional else "0",
    }

    pdf_bytes = generar_pdf(etiquetas, formato, imagenes)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=certificado_{contrato_id}.pdf"},
    )
