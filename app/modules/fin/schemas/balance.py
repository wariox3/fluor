from pydantic import BaseModel

class CuentaBalanceItem(BaseModel):
    codigo_cuenta_fk: int
    nombre: str
    vr_saldo_anterior: float
    vr_debito: float
    vr_credito: float
    vr_saldo_cuenta: float
