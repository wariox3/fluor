from sqlalchemy.orm import Session

from app.modules.tte.models.condicion import Condicion
from app.modules.tte.models.condicion_flete import CondicionFlete
from app.modules.tte.models.condicion_manejo import CondicionManejo
from app.modules.tte.models.precio_detalle import PrecioDetalle


def _buscar_precio_detalle(db: Session, precio, origen, destino, producto, zona):
    """Replica TtePrecioDetalleRepository::apiWindowsDetalleProducto."""
    if not (precio and origen and destino and producto):
        return None
    base = db.query(PrecioDetalle).filter(
        PrecioDetalle.codigo_precio_fk == precio,
        PrecioDetalle.codigo_ciudad_origen_fk == origen,
        PrecioDetalle.codigo_producto_fk == producto,
    )
    # 1) origen + destino
    detalle = base.filter(PrecioDetalle.codigo_ciudad_destino_fk == destino).first()
    if detalle:
        return detalle
    # 2) origen + zona
    if zona:
        detalle = base.filter(PrecioDetalle.codigo_zona_fk == zona).first()
        if detalle:
            return detalle
    # 3) origen + zona NULL
    return base.filter(PrecioDetalle.codigo_zona_fk.is_(None)).first()


def _buscar_condicion_flete(db: Session, tercero, origen, destino, zona, cobertura, pago=None):
    """Replica TteCondicionFleteRepository::apiWindowsLiquidar."""
    if not tercero:
        return None
    base = db.query(CondicionFlete).filter(CondicionFlete.codigo_tercero_fk == tercero)
    if not base.first():
        return None
    if origen and destino:
        cf = base.filter(
            CondicionFlete.codigo_ciudad_origen_fk == origen,
            CondicionFlete.codigo_ciudad_destino_fk == destino,
        ).first()
        if cf:
            return cf
    if zona:
        cf = base.filter(CondicionFlete.codigo_zona_fk == zona).first()
        if cf:
            return cf
    if origen and cobertura and pago:
        cf = base.filter(
            CondicionFlete.codigo_ciudad_origen_fk == origen,
            CondicionFlete.codigo_cobertura_fk == cobertura,
            CondicionFlete.codigo_pago_fk == pago,
        ).first()
        if cf:
            return cf
    if origen and cobertura:
        cf = base.filter(
            CondicionFlete.codigo_ciudad_origen_fk == origen,
            CondicionFlete.codigo_cobertura_fk == cobertura,
        ).first()
        if cf:
            return cf
    if cobertura:
        cf = base.filter(
            CondicionFlete.codigo_ciudad_origen_fk.is_(None),
            CondicionFlete.codigo_ciudad_destino_fk.is_(None),
            CondicionFlete.codigo_cobertura_fk == cobertura,
        ).first()
        if cf:
            return cf
    return base.filter(
        CondicionFlete.codigo_ciudad_origen_fk == origen,
        CondicionFlete.codigo_ciudad_destino_fk.is_(None),
        CondicionFlete.codigo_zona_fk.is_(None),
    ).first()


def _buscar_condicion_manejo(db: Session, tercero, origen, destino, zona, cobertura, pago=None):
    """Replica TteCondicionManejoRepository::apiWindowsLiquidar."""
    if not tercero:
        return None
    base = db.query(CondicionManejo).filter(CondicionManejo.codigo_tercero_fk == tercero)
    if not base.first():
        return None
    if origen and destino:
        cm = base.filter(
            CondicionManejo.codigo_ciudad_origen_fk == origen,
            CondicionManejo.codigo_ciudad_destino_fk == destino,
        ).first()
        if cm:
            return cm
    if zona:
        cm = base.filter(CondicionManejo.codigo_zona_fk == zona).first()
        if cm:
            return cm
    if origen and cobertura and pago:
        cm = base.filter(
            CondicionManejo.codigo_ciudad_origen_fk == origen,
            CondicionManejo.codigo_cobertura_fk == cobertura,
            CondicionManejo.codigo_pago_fk == pago,
        ).first()
        if cm:
            return cm
    if origen and cobertura:
        cm = base.filter(
            CondicionManejo.codigo_ciudad_origen_fk == origen,
            CondicionManejo.codigo_cobertura_fk == cobertura,
        ).first()
        if cm:
            return cm
    if cobertura:
        cm = base.filter(
            CondicionManejo.codigo_ciudad_origen_fk.is_(None),
            CondicionManejo.codigo_ciudad_destino_fk.is_(None),
            CondicionManejo.codigo_cobertura_fk == cobertura,
        ).first()
        if cm:
            return cm
    return base.filter(
        CondicionManejo.codigo_ciudad_origen_fk == origen,
        CondicionManejo.codigo_ciudad_destino_fk.is_(None),
        CondicionManejo.codigo_zona_fk.is_(None),
    ).first()


def liquidar(db: Session, tercero, condicion_id, precio, origen, destino, producto, zona, tipo_liquidacion, unidades, peso, volumen, declarado):
    
    descuento_peso = 0
    porcentaje_manejo = 0
    manejo_minimo_unidad = 0
    manejo_minimo_despacho = 0
    peso_minimo_unidad = 0
    peso_minimo_despacho = 0
    flete_minimo_unidad = 0
    flete_minimo_despacho = 0

    flete = 0
    manejo = 0
    peso_facturado = peso
    if volumen > peso_facturado:
        peso_facturado = volumen
    cobertura = None

    # Condición base
    if condicion_id:
        condicion = db.query(Condicion).filter(Condicion.codigo_condicion_pk == condicion_id).first()
        if condicion:
            descuento_peso = condicion.descuento_peso or 0
            porcentaje_manejo = condicion.porcentaje_manejo or 0
            manejo_minimo_unidad = condicion.manejo_minimo_unidad or 0
            manejo_minimo_despacho = condicion.manejo_minimo_despacho or 0
            peso_minimo_unidad = condicion.peso_minimo or 0

    # Precio detalle (define cobertura)
    precio_detalle = _buscar_precio_detalle(db, precio, origen, destino, producto, zona)
    if precio_detalle:
        cobertura = precio_detalle.codigo_cobertura_fk

    # Condición flete (sobreescribe descuentos y mínimos)
    condicion_flete = _buscar_condicion_flete(db, tercero, origen, destino, zona, cobertura)
    if condicion_flete:
        descuento_peso = condicion_flete.descuento_peso or 0
        peso_minimo_unidad = condicion_flete.peso_minimo or 0
        peso_minimo_despacho = condicion_flete.peso_minimo_guia or 0
        flete_minimo_unidad = condicion_flete.flete_minimo or 0
        flete_minimo_despacho = condicion_flete.flete_minimo_guia or 0

    if peso_facturado < peso_minimo_unidad * unidades:
        peso_facturado = peso_minimo_unidad * unidades
    if peso_facturado < peso_minimo_despacho:
        peso_facturado = peso_minimo_despacho

    if precio_detalle:
        if tipo_liquidacion == "K":
            flete = peso_facturado * (precio_detalle.vr_peso or 0)
            if descuento_peso > 0:
                flete -= flete * descuento_peso / 100
        elif tipo_liquidacion == "U":
            flete = unidades * (precio_detalle.vr_unidad or 0)
        elif tipo_liquidacion == "A":
            flete = peso_facturado * (precio_detalle.vr_peso or 0)

        if unidades > 0:
            if flete_minimo_unidad > flete / unidades:
                flete = flete_minimo_unidad * unidades
        if flete_minimo_despacho > flete:
            flete = flete_minimo_despacho

    # Condición manejo
    condicion_manejo = _buscar_condicion_manejo(db, tercero, origen, destino, zona, cobertura)
    if condicion_manejo:
        porcentaje_manejo = condicion_manejo.porcentaje or 0
        manejo_minimo_unidad = condicion_manejo.minimo_unidad or 0
        manejo_minimo_despacho = condicion_manejo.minimo_despacho or 0

    manejo = declarado * porcentaje_manejo / 100
    if manejo_minimo_despacho > manejo:
        manejo = manejo_minimo_despacho
    if manejo_minimo_unidad * unidades > manejo:
        manejo = manejo_minimo_unidad * unidades

    return {
        "error": False,
        "flete": round(flete),
        "manejo": round(manejo),
        "peso_facturado": peso_facturado,
    }
