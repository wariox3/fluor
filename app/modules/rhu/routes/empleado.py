from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import Optional
from sqlalchemy import func
from app.core.tenant_database import get_tenant_db
from app.core.security import get_current_user
from app.modules.rhu.models.empleado import Empleado
from app.modules.rhu.models.contrato import Contrato
from app.modules.rhu.models.pago import Pago
from app.modules.rhu.models.credito import Credito
from app.modules.rhu.models.embargo import Embargo
from app.modules.rhu.schemas.empleado import EmpleadoListResponse, EstudioCreditoResponse, CuotasPorPlazo, PlazoCredito

router = APIRouter()

PORCENTAJE_MAXIMO = 0.30
PAGOS_A_ANALIZAR = 3
MONTO_MAXIMO_CREDITO = 2000000.0
TASA_INTERES_MENSUAL = 0.021


def _calcular_plazo(cuota_disponible: float, n: int) -> PlazoCredito:
    """Calcula monto máximo financiable y cuota real con interés compuesto."""
    r = TASA_INTERES_MENSUAL
    factor = (1 + r) ** n
    if r > 0 and cuota_disponible > 0:
        monto = cuota_disponible * (factor - 1) / (r * factor)
    else:
        monto = cuota_disponible * n
    monto = min(round(monto, 2), MONTO_MAXIMO_CREDITO)
    cuota = round(monto * r * factor / (factor - 1), 2) if monto > 0 else 0.0
    return PlazoCredito(monto_maximo=monto, cuota=cuota)


@router.get("/lista", response_model=EmpleadoListResponse)
def lista(page: int = 1, size: int = 50, numero_identificacion: Optional[str] = None, db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    query = db.query(Empleado)
    if numero_identificacion:
        query = query.filter(Empleado.numero_identificacion.ilike(f"%{numero_identificacion}%"))
    total = query.with_entities(func.count(Empleado.codigo_empleado_pk)).scalar()
    offset = (page - 1) * size
    empleados = query.offset(offset).limit(size).all()
    return EmpleadoListResponse(total=total, page=page, size=size, items=empleados)


@router.get("/estudio-credito", response_model=EstudioCreditoResponse)
def estudio_credito(
    empleado_id: int,
    db: Session = Depends(get_tenant_db),
    current_user: dict = Depends(get_current_user),
):
    empleado = db.query(Empleado).filter(Empleado.codigo_empleado_pk == empleado_id).first()
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    # --- Contrato activo más reciente ---
    contrato = (
        db.query(Contrato)
        .options(joinedload(Contrato.contrato_tipo_rel))
        .filter(
            Contrato.codigo_empleado_fk == empleado_id,
            Contrato.estado_terminado == False,
        )
        .order_by(Contrato.fecha_desde.desc())
        .first()
    )

    contrato_activo = contrato is not None
    fecha_inicio_contrato = contrato.fecha_desde if contrato else None
    tipo_contrato = contrato.contrato_tipo_rel.nombre if (contrato and contrato.contrato_tipo_rel) else None

    antiguedad_meses = 0
    if fecha_inicio_contrato:
        hoy = date.today()
        antiguedad_meses = (hoy.year - fecha_inicio_contrato.year) * 12 + (hoy.month - fecha_inicio_contrato.month)

    # --- Últimos N pagos aprobados y no anulados ---
    pagos = (
        db.query(Pago)
        .filter(
            Pago.codigo_empleado_fk == empleado_id,
            Pago.estado_aprobado == True,
            Pago.estado_anulado == False,
        )
        .order_by(Pago.fecha_hasta.desc())
        .limit(PAGOS_A_ANALIZAR)
        .all()
    )

    pagos_analizados = len(pagos)
    if pagos_analizados > 0:
        ingreso_promedio_devengado = sum(p.vr_devengado or 0 for p in pagos) / pagos_analizados
        ingreso_promedio_deduccion = sum(p.vr_deduccion or 0 for p in pagos) / pagos_analizados
        ingreso_promedio_neto = sum(p.vr_neto or 0 for p in pagos) / pagos_analizados
    else:
        ingreso_promedio_devengado = 0.0
        ingreso_promedio_deduccion = 0.0
        ingreso_promedio_neto = 0.0

    # --- Créditos vigentes (no pagados, no anulados) ---
    creditos_vigentes_q = (
        db.query(Credito)
        .filter(
            Credito.codigo_empleado_fk == empleado_id,
            Credito.estado_pagado == False,
            Credito.estado_anulado == False,
        )
        .all()
    )
    creditos_vigentes = len(creditos_vigentes_q)
    cuota_mensual_comprometida = sum(c.vr_cuota or 0 for c in creditos_vigentes_q)

    # --- Embargos activos ---
    embargos_q = (
        db.query(Embargo)
        .filter(
            Embargo.codigo_empleado_fk == empleado_id,
            Embargo.estado_activo == True,
            Embargo.estado_anulado == False,
        )
        .all()
    )
    embargos_activos = len(embargos_q)
    descuento_embargo_mensual = sum(e.descuento or 0 for e in embargos_q)

    # --- Capacidad ---
    margen_bruto = round(ingreso_promedio_neto * PORCENTAJE_MAXIMO, 2)
    cuota_disponible = round(max(margen_bruto - cuota_mensual_comprometida - descuento_embargo_mensual, 0), 2)
    monto_maximo = CuotasPorPlazo(
        plazo_12=_calcular_plazo(cuota_disponible, 12),
        plazo_24=_calcular_plazo(cuota_disponible, 24),
        plazo_36=_calcular_plazo(cuota_disponible, 36),
    )

    # --- Score (0-100) ---
    score_detalle = {}

    # Antigüedad laboral (30 pts)
    if antiguedad_meses >= 12:
        pts_antiguedad = 30
    elif antiguedad_meses >= 6:
        pts_antiguedad = 20
    elif antiguedad_meses >= 3:
        pts_antiguedad = 10
    else:
        pts_antiguedad = 0
    score_detalle["antiguedad"] = {"meses": antiguedad_meses, "puntos": pts_antiguedad}

    # Tipo contrato (20 pts)
    tipo_lower = (tipo_contrato or "").lower()
    if "indefinido" in tipo_lower or "término indefinido" in tipo_lower:
        pts_contrato = 20
    elif contrato_activo:
        pts_contrato = 10
    else:
        pts_contrato = 0
    score_detalle["tipo_contrato"] = {"tipo": tipo_contrato, "puntos": pts_contrato}

    # Ratio deducción / devengado (20 pts)
    ratio_deduccion = (ingreso_promedio_deduccion / ingreso_promedio_devengado) if ingreso_promedio_devengado > 0 else 1.0
    if ratio_deduccion < 0.20:
        pts_deduccion = 20
    elif ratio_deduccion < 0.40:
        pts_deduccion = 10
    else:
        pts_deduccion = 0
    score_detalle["ratio_deduccion"] = {"ratio": round(ratio_deduccion, 4), "puntos": pts_deduccion}

    # Historial de pagos aprobados (20 pts)
    if pagos_analizados >= PAGOS_A_ANALIZAR:
        pts_pagos = 20
    elif pagos_analizados >= 1:
        pts_pagos = 10
    else:
        pts_pagos = 0
    score_detalle["historial_pagos"] = {"pagos_aprobados": pagos_analizados, "puntos": pts_pagos}

    # Cuenta bancaria registrada (10 pts)
    pts_banco = 10 if empleado.cuenta else 0
    score_detalle["cuenta_bancaria"] = {"tiene_cuenta": bool(empleado.cuenta), "puntos": pts_banco}

    # Embargos activos (penalización)
    if embargos_activos == 0:
        pts_embargo = 0
    elif embargos_activos == 1:
        pts_embargo = -10
    else:
        pts_embargo = -20
    score_detalle["embargos"] = {"embargos_activos": embargos_activos, "puntos": pts_embargo}

    score = max(pts_antiguedad + pts_contrato + pts_deduccion + pts_pagos + pts_banco + pts_embargo, 0)

    return EstudioCreditoResponse(
        codigo_empleado_pk=empleado.codigo_empleado_pk,
        nombre_corto=empleado.nombre_corto,
        numero_identificacion=empleado.numero_identificacion,
        contrato_activo=contrato_activo,
        fecha_inicio_contrato=fecha_inicio_contrato,
        antiguedad_meses=antiguedad_meses,
        tipo_contrato=tipo_contrato,
        pagos_analizados=pagos_analizados,
        ingreso_promedio_devengado=round(ingreso_promedio_devengado, 2),
        ingreso_promedio_deduccion=round(ingreso_promedio_deduccion, 2),
        ingreso_promedio_neto=round(ingreso_promedio_neto, 2),
        creditos_vigentes=creditos_vigentes,
        cuota_mensual_comprometida=round(cuota_mensual_comprometida, 2),
        embargos_activos=embargos_activos,
        descuento_embargo_mensual=round(descuento_embargo_mensual, 2),
        porcentaje_aplicado=PORCENTAJE_MAXIMO,
        margen_bruto=margen_bruto,
        cuota_disponible=cuota_disponible,
        monto_maximo=monto_maximo,
        score=score,
        score_detalle=score_detalle,
    )