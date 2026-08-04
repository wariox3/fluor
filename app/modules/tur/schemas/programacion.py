from pydantic import BaseModel
from typing import List, Optional


class ProgramacionResponse(BaseModel):
    codigo_programacion_pk: int
    codigo_pedido_fk: Optional[int] = None
    codigo_pedido_detalle_fk: Optional[int] = None
    codigo_puesto_fk: Optional[int] = None
    codigo_empleado_fk: Optional[int] = None
    codigo_contrato_fk: Optional[int] = None
    anio: Optional[int] = None
    mes: Optional[int] = None
    dia_1: Optional[str] = None
    dia_2: Optional[str] = None
    dia_3: Optional[str] = None
    dia_4: Optional[str] = None
    dia_5: Optional[str] = None
    dia_6: Optional[str] = None
    dia_7: Optional[str] = None
    dia_8: Optional[str] = None
    dia_9: Optional[str] = None
    dia_10: Optional[str] = None
    dia_11: Optional[str] = None
    dia_12: Optional[str] = None
    dia_13: Optional[str] = None
    dia_14: Optional[str] = None
    dia_15: Optional[str] = None
    dia_16: Optional[str] = None
    dia_17: Optional[str] = None
    dia_18: Optional[str] = None
    dia_19: Optional[str] = None
    dia_20: Optional[str] = None
    dia_21: Optional[str] = None
    dia_22: Optional[str] = None
    dia_23: Optional[str] = None
    dia_24: Optional[str] = None
    dia_25: Optional[str] = None
    dia_26: Optional[str] = None
    dia_27: Optional[str] = None
    dia_28: Optional[str] = None
    dia_29: Optional[str] = None
    dia_30: Optional[str] = None
    dia_31: Optional[str] = None
    horas: Optional[float] = None
    horas_diurnas: Optional[float] = None
    horas_nocturnas: Optional[float] = None
    complementario: Optional[bool] = None
    adicional: Optional[bool] = None
    periodo_bloqueo: Optional[int] = None
    reporte: Optional[bool] = None
    recursivo: Optional[bool] = None
    puesto_nombre: Optional[str] = None
    empleado_nombre: Optional[str] = None
    empleado_celular: Optional[str] = None
    codigo_tercero_fk: Optional[int] = None
    tercero_nombre: Optional[str] = None
    zona_nombre: Optional[str] = None
    subzona_nombre: Optional[str] = None
    cargo_nombre: Optional[str] = None
    grupo_nombre: Optional[str] = None
    estado_contrato: Optional[bool] = None

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_with_rels(cls, obj):
        data = cls.model_validate(obj)
        if obj.puesto_rel:
            data.puesto_nombre = obj.puesto_rel.nombre
            if obj.puesto_rel.zona_rel:
                data.zona_nombre = obj.puesto_rel.zona_rel.nombre
            if obj.puesto_rel.subzona_rel:
                data.subzona_nombre = obj.puesto_rel.subzona_rel.nombre
        if obj.empleado_rel:
            data.empleado_nombre = obj.empleado_rel.nombre_corto
            data.empleado_celular = obj.empleado_rel.celular
            data.estado_contrato = obj.empleado_rel.estado_contrato
        if obj.contrato_rel:
            if obj.contrato_rel.cargo_rel:
                data.cargo_nombre = obj.contrato_rel.cargo_rel.nombre
            if obj.contrato_rel.grupo_rel:
                data.grupo_nombre = obj.contrato_rel.grupo_rel.nombre
        if obj.pedido_detalle_rel and obj.pedido_detalle_rel.pedido_rel:
            data.codigo_tercero_fk = obj.pedido_detalle_rel.pedido_rel.codigo_tercero_fk
            if obj.pedido_detalle_rel.pedido_rel.tercero_rel:
                data.tercero_nombre = obj.pedido_detalle_rel.pedido_rel.tercero_rel.nombre_corto
        return data


class ProgramacionListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[ProgramacionResponse]


class ProgramacionItem(BaseModel):
    codigo_programacion_pk: int
    codigo_puesto_fk: Optional[int] = None
    puesto_nombre: Optional[str] = None
    puesto_direccion: Optional[str] = None
    coordinador_nombre: Optional[str] = None
    programador_nombre: Optional[str] = None
    codigo_modalidad_fk: Optional[str] = None
    tercero_nombre_corto: Optional[str] = None
    dia_1: Optional[str] = None
    dia_2: Optional[str] = None
    dia_3: Optional[str] = None
    dia_4: Optional[str] = None
    dia_5: Optional[str] = None
    dia_6: Optional[str] = None
    dia_7: Optional[str] = None
    dia_8: Optional[str] = None
    dia_9: Optional[str] = None
    dia_10: Optional[str] = None
    dia_11: Optional[str] = None
    dia_12: Optional[str] = None
    dia_13: Optional[str] = None
    dia_14: Optional[str] = None
    dia_15: Optional[str] = None
    dia_16: Optional[str] = None
    dia_17: Optional[str] = None
    dia_18: Optional[str] = None
    dia_19: Optional[str] = None
    dia_20: Optional[str] = None
    dia_21: Optional[str] = None
    dia_22: Optional[str] = None
    dia_23: Optional[str] = None
    dia_24: Optional[str] = None
    dia_25: Optional[str] = None
    dia_26: Optional[str] = None
    dia_27: Optional[str] = None
    dia_28: Optional[str] = None
    dia_29: Optional[str] = None
    dia_30: Optional[str] = None
    dia_31: Optional[str] = None
