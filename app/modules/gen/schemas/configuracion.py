from typing import Optional

from pydantic import BaseModel


class ConfiguracionGuiaNuevoResponse(BaseModel):
    codigo_precio_general_fk: Optional[int] = None
    codigo_condicion_general_fk: Optional[int] = None
    codigo_asesor_general_fk: Optional[int] = None

    model_config = {"from_attributes": True}
