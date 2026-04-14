from pydantic import BaseModel


class CuentaBalanceItem(BaseModel):
    codigo_cuenta_fk: int
    nombre: str
    vr_saldo_anterior: float
    vr_debito: float
    vr_credito: float
    vr_saldo_cuenta: float


class CentroCostoBalanceItem(BaseModel):
    codigo_periodo_fk: int
    codigo_cuenta_fk: str
    codigo_centro_costo_fk: str
    vr_debito: float
    vr_credito: float
