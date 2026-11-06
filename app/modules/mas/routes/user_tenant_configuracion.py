from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.master_database import get_master_db
from app.core.security import get_current_user_from_token
from app.modules.mas.models.user_tenant import UserTenant, es_control
from app.modules.mas.models.user_tenant_configuracion import UserTenantConfiguracion
from app.modules.mas.schemas.user_tenant_configuracion import (
    UserTenantConfiguracionActualizarRequest,
    UserTenantConfiguracionResponse,
)

router = APIRouter()


def _membresia(db: Session, user_tenant_id: int) -> UserTenant:
    ut = db.query(UserTenant).filter(UserTenant.id == user_tenant_id).first()
    if not ut:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Membresía no encontrada")
    return ut


# Valores de la tabla cuando la membresía aún no tiene fila de configuración
_POR_DEFECTO = {
    "cambiar_valores_guia": False,
    "permite_cambiar_adquiriente": False,
    "estado_recogido": True,
    "estado_ingreso": True,
    "invertir_origen_destino": False,
    "bloquear_recaudo": False,
    "bloquear_adquiriente_credito": False,
    "bloquear_operacion_cliente": False,
}


def _respuesta(ut: UserTenant) -> UserTenantConfiguracionResponse:
    """Configuración de la membresía; si aún no tiene: códigos en null y booleanos con su valor por defecto."""
    c = ut.configuracion
    return UserTenantConfiguracionResponse(
        user_tenant_id=ut.id,
        codigo_operacion_fk=c.codigo_operacion_fk if c else None,
        codigo_tercero_operacion_fk=c.codigo_tercero_operacion_fk if c else None,
        codigo_ciudad_origen_fk=c.codigo_ciudad_origen_fk if c else None,
        **{campo: getattr(c, campo) if c else defecto for campo, defecto in _POR_DEFECTO.items()},
    )


@router.get("/{user_tenant_id}", response_model=UserTenantConfiguracionResponse, include_in_schema=False)
def detalle(
    user_tenant_id: int,
    db: Session = Depends(get_master_db),
    current_user: dict = Depends(get_current_user_from_token),
):
    """Configuración de una membresía. Para el dueño de la membresía o quien es control activo en esa empresa."""
    ut = _membresia(db, user_tenant_id)
    usuario_id = int(current_user["sub"])
    if ut.usuario_id != usuario_id and not es_control(db, usuario_id, ut.tenant_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para ver esta configuración")
    return _respuesta(ut)


@router.patch("/{user_tenant_id}/actualizar", response_model=UserTenantConfiguracionResponse, include_in_schema=False)
def actualizar(
    user_tenant_id: int,
    data: UserTenantConfiguracionActualizarRequest,
    db: Session = Depends(get_master_db),
    current_user: dict = Depends(get_current_user_from_token),
):
    """Actualiza la configuración de una membresía (solo los campos enviados); la crea si no existe.
    Solo para quien es control activo en esa empresa."""
    ut = _membresia(db, user_tenant_id)
    if not es_control(db, int(current_user["sub"]), ut.tenant_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para actualizar usuarios de esta empresa")

    if ut.configuracion is None:
        ut.configuracion = UserTenantConfiguracion()
    for campo, valor in data.model_dump(exclude_unset=True).items():
        setattr(ut.configuracion, campo, valor)
    db.commit()
    db.refresh(ut)
    return _respuesta(ut)
