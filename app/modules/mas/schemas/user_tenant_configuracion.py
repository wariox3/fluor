from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class UserTenantConfiguracionActualizarRequest(BaseModel):
    """Actualización parcial: solo se cambian los campos enviados.
    En los códigos, null (o "") los limpia; los booleanos no aceptan null."""
    model_config = ConfigDict(extra="forbid")

    codigo_operacion_fk: str | None = Field(default=None, max_length=20)
    codigo_tercero_operacion_fk: int | None = None
    codigo_ciudad_origen_fk: str | None = Field(default=None, max_length=20)
    cambiar_valores_guia: bool = False
    permite_cambiar_adquiriente: bool = False
    estado_recogido: bool = True
    estado_ingreso: bool = True
    invertir_origen_destino: bool = False
    bloquear_recaudo: bool = False
    bloquear_adquiriente_credito: bool = False
    bloquear_operacion_cliente: bool = False

    @field_validator("codigo_operacion_fk", "codigo_ciudad_origen_fk")
    @classmethod
    def _vacio_a_none(cls, v: str | None) -> str | None:
        if v is None:
            return None
        v = v.strip()
        return v or None

    @model_validator(mode="after")
    def _al_menos_un_campo(self):
        if not self.model_fields_set:
            raise ValueError("Envía al menos un campo para actualizar")
        return self


class UserTenantConfiguracionResponse(BaseModel):
    user_tenant_id: int
    codigo_operacion_fk: str | None
    codigo_tercero_operacion_fk: int | None
    codigo_ciudad_origen_fk: str | None
    cambiar_valores_guia: bool
    permite_cambiar_adquiriente: bool
    estado_recogido: bool
    estado_ingreso: bool
    invertir_origen_destino: bool
    bloquear_recaudo: bool
    bloquear_adquiriente_credito: bool
    bloquear_operacion_cliente: bool
