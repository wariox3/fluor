from pydantic import BaseModel, EmailStr, Field, field_validator


class SolicitudTipoPortalResponse(BaseModel):
    """Tipo de PQRS que el cliente puede registrar desde el portal."""

    codigo_solicitud_tipo_pk: str
    nombre: str

    model_config = {"from_attributes": True}


class SolicitudPortalNuevoRequest(BaseModel):
    """PQRS nueva del cliente; el tercero es el cliente de su membresía y el canal, el portal."""

    model_config = {"extra": "forbid"}

    codigo_solicitud_tipo_fk: str = Field(min_length=1, max_length=10)
    descripcion: str = Field(min_length=1, max_length=5000)
    # Contacto que registra la PQRS (longitudes de `crm_solicitud`)
    nombre_contacto: str | None = Field(default=None, max_length=80)
    numero_identificacion_contacto: str | None = Field(default=None, max_length=80)
    telefono_contacto: str | None = Field(default=None, max_length=50)
    correo_contacto: EmailStr | None = Field(default=None, max_length=100)
    cargo_contacto: str | None = Field(default=None, max_length=50)

    @field_validator(
        "nombre_contacto",
        "numero_identificacion_contacto",
        "telefono_contacto",
        "correo_contacto",
        "cargo_contacto",
        mode="before",
    )
    @classmethod
    def _vacio_a_none(cls, v: str | None) -> str | None:
        if v is None:
            return None
        v = str(v).strip()
        return v or None

    @field_validator("descripcion")
    @classmethod
    def _descripcion_sin_espacios(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("La descripción es obligatoria")
        return v
