from pydantic import BaseModel
from typing import List, Optional


class FormatoContenidoUpdate(BaseModel):
    contenido_externo: Optional[str] = None


class FormatoResponse(BaseModel):
    codigo_formato_pk: int
    nombre: Optional[str] = None
    titulo: Optional[str] = None
    contenido: Optional[str] = None
    contenido_externo: Optional[str] = None
    etiquetas: Optional[str] = None
    tamano_papel: Optional[str] = None
    orientacion_papel: Optional[str] = None
    tamanio_fuente: Optional[str] = None
    nombre_firma: Optional[str] = None
    cargo_firma: Optional[str] = None
    nombre_firma_otro: Optional[str] = None
    cargo_firma_otro: Optional[str] = None
    nombre_firma_otro_dos: Optional[str] = None
    cargo_firma_otro_dos: Optional[str] = None
    nombre_empresa: Optional[bool] = None
    nit_empresa: Optional[bool] = None
    huella: Optional[bool] = None
    codigo_modelo_fk: Optional[str] = None
    version: Optional[str] = None
    codigo: Optional[str] = None

    model_config = {"from_attributes": True}


class FormatoListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[FormatoResponse]
