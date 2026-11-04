from sqlalchemy.orm import Session

from app.modules.gen.models.tercero import Tercero
from app.modules.tte.models.ciudad import Ciudad
from app.modules.tte.models.condicion import Condicion
from app.modules.tte.models.condicion_flete import CondicionFlete
from app.modules.tte.models.condicion_manejo import CondicionManejo
from app.modules.tte.models.guia_tipo import GuiaTipo
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


def buscar_condicion_flete(db: Session, tercero, origen, destino, zona, cobertura, pago=None):
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
    # Sin origen se omite: "== None" se volvería IS NULL y traería otra condición
    if not origen:
        return None
    return base.filter(
        CondicionFlete.codigo_ciudad_origen_fk == origen,
        CondicionFlete.codigo_ciudad_destino_fk.is_(None),
        CondicionFlete.codigo_zona_fk.is_(None),
    ).first()


def buscar_condicion_manejo(db: Session, tercero, origen, destino, zona, cobertura, pago=None):
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
    # Sin origen se omite: "== None" se volvería IS NULL y traería otra condición
    if not origen:
        return None
    return base.filter(
        CondicionManejo.codigo_ciudad_origen_fk == origen,
        CondicionManejo.codigo_ciudad_destino_fk.is_(None),
        CondicionManejo.codigo_zona_fk.is_(None),
    ).first()


def condicion_especial(db: Session, tercero, origen, destino, precio, guia_tipo=None, producto=None):
    """Replica TteGuiaRepository::condicionEspecial de PHP.
    Devuelve None si el tercero no existe."""
    tercero_obj = db.query(Tercero).filter(Tercero.codigo_tercero_pk == tercero).first()
    if not tercero_obj:
        return None

    resultado = {
        "error": False,
        "error_mensaje": None,
        "condicion_especial_flete": False,
        "condicion_especial_manejo": False,
        "cobertura": None,
        "vr_peso": 0,
        "vr_unidad": 0,
        "descuento_peso": 0,
        "descuento_unidad": 0,
        "peso_minimo": 0,
        "peso_minimo_guia": 0,
        "flete_minimo": 0,
        "flete_minimo_guia": 0,
        "porcentaje_manejo": 0,
        "manejo_minimo_unidad": 0,
        "manejo_minimo_guia": 0,
        "reexpedicion": False,
    }

    pago = None
    if guia_tipo:
        tipo = db.query(GuiaTipo).filter(GuiaTipo.codigo_guia_tipo_pk == guia_tipo).first()
        if tipo:
            pago = tipo.codigo_pago_fk

    # Manejo base desde la condición del tercero
    condicion = tercero_obj.condicion
    if condicion:
        resultado["porcentaje_manejo"] = condicion.porcentaje_manejo or 0
        resultado["manejo_minimo_unidad"] = condicion.manejo_minimo_unidad or 0
        resultado["manejo_minimo_guia"] = condicion.manejo_minimo_despacho or 0

    zona = None
    ciudad_destino = db.query(Ciudad).filter(Ciudad.codigo_ciudad_pk == destino).first()
    if ciudad_destino:
        resultado["reexpedicion"] = bool(ciudad_destino.reexpedicion)
        zona = ciudad_destino.codigo_zona_fk

    if producto:
        precio_detalle = _buscar_precio_detalle(db, precio, origen, destino, producto, zona)
        if precio_detalle:
            resultado["vr_peso"] = precio_detalle.vr_peso or 0
            resultado["vr_unidad"] = precio_detalle.vr_unidad or 0
            resultado["cobertura"] = precio_detalle.codigo_cobertura_fk
            resultado["peso_minimo"] = precio_detalle.minimo or 0
    else:
        resultado["error"] = True
        resultado["error_mensaje"] = "Debe indicar el producto"

    cobertura = resultado["cobertura"]

    condicion_flete = buscar_condicion_flete(db, tercero, origen, destino, zona, cobertura, pago)
    if condicion_flete:
        resultado["condicion_especial_flete"] = True
        resultado["descuento_peso"] = condicion_flete.descuento_peso or 0
        resultado["descuento_unidad"] = condicion_flete.descuento_unidad or 0
        resultado["peso_minimo"] = condicion_flete.peso_minimo or 0
        resultado["peso_minimo_guia"] = condicion_flete.peso_minimo_guia or 0
        resultado["flete_minimo"] = condicion_flete.flete_minimo or 0
        resultado["flete_minimo_guia"] = condicion_flete.flete_minimo_guia or 0

    condicion_manejo = buscar_condicion_manejo(db, tercero, origen, destino, zona, cobertura, pago)
    if condicion_manejo:
        resultado["condicion_especial_manejo"] = True
        resultado["porcentaje_manejo"] = condicion_manejo.porcentaje or 0
        resultado["manejo_minimo_unidad"] = condicion_manejo.minimo_unidad or 0
        resultado["manejo_minimo_guia"] = condicion_manejo.minimo_despacho or 0

    return resultado


def liquidar(db: Session, tercero, condicion_id, precio, origen, destino, producto, zona, tipo_liquidacion, unidades, peso, volumen, declarado, pago=None):
    
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
    condicion_flete = buscar_condicion_flete(db, tercero, origen, destino, zona, cobertura, pago)
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
    condicion_manejo = buscar_condicion_manejo(db, tercero, origen, destino, zona, cobertura, pago)
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
