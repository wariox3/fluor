from pydantic import BaseModel

class GuiaBase(BaseModel):
    documento_cliente: str

class GuiaResponse(GuiaBase):
    codigo_guia_pk: int

    class Config:
        from_attributes = True