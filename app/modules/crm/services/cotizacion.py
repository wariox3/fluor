"""
Liquidación de las cotizaciones de servicios de vigilancia.

Replica la lógica de holmio que usaba el portal de clientes de terbio:
- `FuncionesController::horaServicio` → `hora_servicio`
- `FuncionesController::horarioTurno` → `horario_turno`
- `CrmCotizacionRepository::liquidarServicios` → `liquidar_servicios`
"""

from dataclasses import dataclass
from datetime import date, time, timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.modules.crm.models.cotizacion import Cotizacion
from app.modules.crm.models.cotizacion_detalle import CotizacionDetalle
from app.modules.gen.models.configuracion import Configuracion
from app.modules.tur.models.festivo import Festivo
from app.modules.tur.models.sector import Sector

# Desde esta fecha la jornada nocturna empieza a las 19:00 (13 horas diurnas y 11 nocturnas)
FECHA_DECRETO_JORNADA = date(2025, 12, 26)

# Sector residencial: la modalidad usa su porcentaje residencial
SECTOR_RESIDENCIAL = "RES"

# Días que holmio cuenta en un mes de servicio (periodo M)
DIAS_ORDINARIOS_POR_DIA_SEMANA = 4
DIAS_SABADO = 4
DIAS_DOMINGO = 4
DIAS_FESTIVO = 2
DIAS_MES = 30

# Reparto del valor del servicio entre las horas diurnas y nocturnas
PORCENTAJE_VALOR_DIURNO = 47.59
PORCENTAJE_VALOR_NOCTURNO = 52.41


@dataclass(frozen=True)
class HorasServicio:
    """Horas de un día de servicio."""

    horas: float
    diurnas: float
    nocturnas: float


def _calcular_tiempo(inicio: float, fin: float, rango_inicio: float, rango_fin: float) -> float:
    """Horas de [inicio, fin] que caen dentro de [rango_inicio, rango_fin]."""
    desde = max(inicio, rango_inicio)
    if fin > rango_fin:
        hasta = inicio if inicio > rango_fin else rango_fin
    else:
        hasta = fin if fin > rango_inicio else rango_inicio
    return hasta - desde


def _hora_decimal(valor: time) -> float:
    return valor.hour + valor.minute / 60


def hora_servicio(hora_desde: time, hora_hasta: time, fecha: date) -> HorasServicio:
    """Horas diurnas y nocturnas de un turno. 00:00 a 00:00 es un turno de 24 horas."""
    if fecha >= FECHA_DECRETO_JORNADA:
        diurnas_dia, nocturnas_dia, inicia_noche = 13, 11, 19
    else:
        diurnas_dia, nocturnas_dia, inicia_noche = 15, 9, 21

    inicio = _hora_decimal(hora_desde)
    fin = _hora_decimal(hora_hasta)
    if inicio == 0 and fin == 0:
        return HorasServicio(horas=24, diurnas=diurnas_dia, nocturnas=nocturnas_dia)

    # Tramos: madrugada (0-6), día (6-noche) y noche (noche-24)
    def tramo(desde: float, hasta: float) -> tuple[float, float]:
        diurnas = _calcular_tiempo(desde, hasta, 6, inicia_noche)
        nocturnas = _calcular_tiempo(desde, hasta, 0, 6) + _calcular_tiempo(desde, hasta, inicia_noche, 24)
        return diurnas, nocturnas

    if inicio < fin:
        diurnas, nocturnas = tramo(inicio, fin)
    else:
        # El turno pasa la medianoche
        diurnas_inicio, nocturnas_inicio = tramo(inicio, 24)
        diurnas_fin, nocturnas_fin = tramo(0, fin)
        diurnas = diurnas_inicio + diurnas_fin
        nocturnas = nocturnas_inicio + nocturnas_fin
    return HorasServicio(horas=diurnas + nocturnas, diurnas=diurnas, nocturnas=nocturnas)


def horario_turno(detalle: CotizacionDetalle) -> str:
    """Texto del horario, p. ej. "06:00 a 18:00 lunes a viernes" o "24 horas lunes a domingo + festivos"."""
    if detalle.compuesto:
        return ""
    desde = detalle.hora_desde.strftime("%H:%M")
    hasta = detalle.hora_hasta.strftime("%H:%M")
    horario = "24 horas" if desde == "00:00" and hasta == "00:00" else f"{desde} a {hasta}"

    d = detalle
    if all((d.lunes, d.martes, d.miercoles, d.jueves, d.viernes, d.sabado, d.domingo)):
        horario += " lunes a domingo"
        if d.festivo:
            horario += " + festivos"
    elif all((d.lunes, d.martes, d.miercoles, d.jueves, d.viernes, d.sabado)):
        horario += " lunes a sabado"
    elif all((d.lunes, d.martes, d.miercoles, d.jueves, d.viernes)):
        horario += " lunes a viernes"
    elif all((d.lunes, d.martes, d.miercoles, d.jueves)):
        horario += " lunes a jueves"
    elif all((d.lunes, d.martes, d.miercoles)):
        horario += " lunes a miercoles"
    else:
        dias = [
            nombre
            for nombre, activo in (
                ("lunes", d.lunes), ("martes", d.martes), ("miercoles", d.miercoles),
                ("jueves", d.jueves), ("viernes", d.viernes), ("sabado", d.sabado),
                ("domingo", d.domingo), ("festivo", d.festivo),
            )
            if activo
        ]
        if dias:
            horario += " " + " ".join(dias)
    return horario


def _dia_activo(detalle: CotizacionDetalle, dia: date, festivos: set[date]) -> bool:
    """Si el servicio se presta ese día (los festivos dependen solo de la marca de festivo)."""
    if dia in festivos:
        return bool(detalle.festivo)
    dias_semana = (
        detalle.lunes, detalle.martes, detalle.miercoles, detalle.jueves,
        detalle.viernes, detalle.sabado, detalle.domingo,
    )
    return bool(dias_semana[dia.weekday()])


def _horas_periodo(db: Session, detalle: CotizacionDetalle) -> tuple[float, float]:
    """Horas diurnas y nocturnas de una unidad del servicio en su periodo."""
    diurnas_unidad = detalle.horas_diurnas_unidad or 0
    nocturnas_unidad = detalle.horas_nocturnas_unidad or 0

    if detalle.periodo == "M":
        dias = DIAS_ORDINARIOS_POR_DIA_SEMANA * sum(
            bool(v) for v in (detalle.lunes, detalle.martes, detalle.miercoles, detalle.jueves, detalle.viernes)
        )
        dias += DIAS_SABADO if detalle.sabado else 0
        dias += DIAS_DOMINGO if detalle.domingo else 0
        dias += DIAS_FESTIVO if detalle.festivo else 0
        return diurnas_unidad * dias, nocturnas_unidad * dias

    # Periodo por días: se recorre cada día entre las fechas, con los festivos de la empresa
    if not detalle.fecha_desde or not detalle.fecha_hasta:
        return 0, 0
    festivos = {
        f.fecha
        for f in db.query(Festivo.fecha).filter(
            Festivo.fecha >= detalle.fecha_desde, Festivo.fecha <= detalle.fecha_hasta
        )
    }
    dias_activos = sum(
        _dia_activo(detalle, detalle.fecha_desde + timedelta(days=i), festivos)
        for i in range((detalle.fecha_hasta - detalle.fecha_desde).days + 1)
    )
    return diurnas_unidad * dias_activos, nocturnas_unidad * dias_activos


def liquidar_servicios(db: Session, cotizacion: Cotizacion) -> None:
    """Recalcula horas y valores de cada servicio vigente y los totales de la cotización.

    No hace commit: el llamador confirma la transacción.
    """
    sector = db.get(Sector, cotizacion.codigo_sector_fk) if cotizacion.codigo_sector_fk else None
    if not sector:
        raise HTTPException(status_code=400, detail="La cotización no tiene un sector válido")
    configuracion = db.query(Configuracion.liquidar_especial_cotizacion).first()
    liquidar_especial = bool(configuracion and configuracion.liquidar_especial_cotizacion)

    detalles = (
        db.query(CotizacionDetalle)
        .filter(
            CotizacionDetalle.codigo_cotizacion_fk == cotizacion.codigo_cotizacion_pk,
            CotizacionDetalle.estado_terminado.is_(False),
        )
        .all()
    )

    total_horas = total_diurnas = total_nocturnas = 0.0
    total_servicio = total_minimo = 0.0
    subtotal_general = base_aiu_general = iva_general = total_general = 0.0

    for detalle in detalles:
        cantidad = detalle.cantidad or 0
        diurnas, nocturnas = _horas_periodo(db, detalle)
        diurnas *= cantidad
        nocturnas *= cantidad
        horas = diurnas + nocturnas

        valor_base = (detalle.vr_salario_base or 0) * (sector.porcentaje or 0) + (detalle.vr_precio_adicional or 0)
        modalidad = detalle.modalidad_rel
        if cotizacion.codigo_sector_fk == SECTOR_RESIDENCIAL:
            porcentaje_modalidad = (modalidad.porcentaje_residencial if modalidad else 0) or 0
        else:
            porcentaje_modalidad = (modalidad.porcentaje if modalidad else 0) or 0
        valor_base_mes = valor_base + valor_base * porcentaje_modalidad / 100
        valor_hora_diurna = valor_base_mes * PORCENTAJE_VALOR_DIURNO / 100 / DIAS_MES / 13
        valor_hora_nocturna = valor_base_mes * PORCENTAJE_VALOR_NOCTURNO / 100 / DIAS_MES / 11

        valor_horas = diurnas * valor_hora_diurna + nocturnas * valor_hora_nocturna
        if liquidar_especial and cantidad:
            # Precio por unidad: el servicio se cobra por cantidad
            precio = valor_horas / cantidad
            valor_minimo = precio
            valor_servicio = valor_minimo * cantidad
        else:
            precio = valor_horas
            valor_minimo = precio
            valor_servicio = valor_minimo

        if detalle.vr_precio_ajustado:
            valor_servicio = detalle.vr_precio_ajustado * cantidad
            precio = detalle.vr_precio_ajustado

        subtotal = valor_servicio
        base_aiu = subtotal * (detalle.porcentaje_base_iva or 0) / 100
        iva = base_aiu * (detalle.porcentaje_iva or 0) / 100
        total = subtotal + iva

        detalle.vr_subtotal = subtotal
        detalle.vr_base_aiu = base_aiu
        detalle.vr_iva = iva
        detalle.vr_total_detalle = total
        detalle.vr_precio_minimo = valor_minimo
        detalle.vr_precio = precio
        detalle.horas = horas
        detalle.horas_diurnas = diurnas
        detalle.horas_nocturnas = nocturnas

        subtotal_general += subtotal
        base_aiu_general += base_aiu
        iva_general += iva
        total_general += total
        total_horas += horas
        total_diurnas += diurnas
        total_nocturnas += nocturnas
        total_minimo += valor_minimo
        total_servicio += valor_servicio

    # En la cotización las horas son enteras
    cotizacion.horas = round(total_horas)
    cotizacion.horas_diurnas = round(total_diurnas)
    cotizacion.horas_nocturnas = round(total_nocturnas)
    cotizacion.vr_total_servicio = total_servicio
    cotizacion.vr_total_precio_minimo = total_minimo
    cotizacion.vr_total_costo = 0
    cotizacion.vr_subtotal = subtotal_general
    cotizacion.vr_base_aiu = base_aiu_general
    cotizacion.vr_iva = iva_general
    cotizacion.vr_total = total_general
