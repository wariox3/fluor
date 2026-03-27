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

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_with_rels(cls, obj):
        data = cls.model_validate(obj)
        if obj.puesto_rel:
            data.puesto_nombre = obj.puesto_rel.nombre
        if obj.empleado_rel:
            data.empleado_nombre = obj.empleado_rel.nombre_corto
        return data


class ProgramacionListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[ProgramacionResponse]


class ProgramacionItem(BaseModel):
    codigo_programacion_pk: int
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
