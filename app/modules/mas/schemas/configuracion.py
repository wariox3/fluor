from pydantic import BaseModel


class ConfiguracionResponse(BaseModel):
    codigo_configuracion_pk: int
    tasa_interes: float

    model_config = {"from_attributes": True}


class ConfiguracionActualizar(BaseModel):
    tasa_interes: float
