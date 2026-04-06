from pydantic import BaseModel
from decimal import Decimal


class ConfiguracionResponse(BaseModel):
    codigo_configuracion_pk: int
    tasa_interes: Decimal

    model_config = {"from_attributes": True}


class ConfiguracionActualizar(BaseModel):
    tasa_interes: Decimal
