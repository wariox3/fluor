from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.core.tenant_database import get_tenant_db
from app.core.utils import Filtro, ListaConfig, paginar
from app.modules.gen.models.log_accion import LogAccion
from app.modules.gen.schemas.log_accion import LogAccionListResponse

router = APIRouter()


LISTA_LOG_ACCION = ListaConfig(
    pk=LogAccion.codigo_log_accion_pk,
    # Lo más reciente primero
    orden=[LogAccion.fecha.desc(), LogAccion.codigo_log_accion_pk.desc()],
    filtros={
        "codigo_modelo_fk": Filtro(LogAccion.codigo_modelo_fk, descripcion="Código de gen_modelo, ej. TteGuia"),
        "codigo_registro": Filtro(LogAccion.codigo_registro, descripcion="Id del registro auditado"),
        "accion": Filtro(LogAccion.accion, descripcion="crear, editar o eliminar"),
        "usuario": Filtro(LogAccion.usuario, "contiene"),
        "fecha_desde": Filtro(LogAccion.fecha, "gte", tipo=date, descripcion="Fecha desde"),
        "fecha_hasta": Filtro(LogAccion.fecha, "hasta_dia", tipo=date, descripcion="Fecha hasta (incluye el día)"),
    },
)


@router.get("/lista", response_model=LogAccionListResponse)
def lista(params: dict = Depends(LISTA_LOG_ACCION.params_lista), db: Session = Depends(get_tenant_db), current_user: dict = Depends(get_current_user)):
    """Historial de cambios auditados. Para el historial de un registro: ?codigo_modelo_fk=TteGuia&codigo_registro=123"""
    return paginar(db, LISTA_LOG_ACCION, params)
