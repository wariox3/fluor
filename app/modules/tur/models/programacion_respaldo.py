from sqlalchemy import Column, Integer, String
from app.core.tenant_database import Base


class ProgramacionRespaldo(Base):
    __tablename__ = "tur_programacion_respaldo"

    codigo_programacion_respaldo_pk = Column(Integer, primary_key=True, index=True)
    codigo_soporte_contrato_fk = Column(Integer, nullable=True)
    codigo_empleado_fk = Column(Integer, nullable=True)
    anio = Column(Integer, nullable=True)
    mes = Column(Integer, nullable=True)

    dia_1  = Column("dia_1",  String(5), nullable=True)
    dia_2  = Column("dia_2",  String(5), nullable=True)
    dia_3  = Column("dia_3",  String(5), nullable=True)
    dia_4  = Column("dia_4",  String(5), nullable=True)
    dia_5  = Column("dia_5",  String(5), nullable=True)
    dia_6  = Column("dia_6",  String(5), nullable=True)
    dia_7  = Column("dia_7",  String(5), nullable=True)
    dia_8  = Column("dia_8",  String(5), nullable=True)
    dia_9  = Column("dia_9",  String(5), nullable=True)
    dia_10 = Column("dia_10", String(5), nullable=True)
    dia_11 = Column("dia_11", String(5), nullable=True)
    dia_12 = Column("dia_12", String(5), nullable=True)
    dia_13 = Column("dia_13", String(5), nullable=True)
    dia_14 = Column("dia_14", String(5), nullable=True)
    dia_15 = Column("dia_15", String(5), nullable=True)
    dia_16 = Column("dia_16", String(5), nullable=True)
    dia_17 = Column("dia_17", String(5), nullable=True)
    dia_18 = Column("dia_18", String(5), nullable=True)
    dia_19 = Column("dia_19", String(5), nullable=True)
    dia_20 = Column("dia_20", String(5), nullable=True)
    dia_21 = Column("dia_21", String(5), nullable=True)
    dia_22 = Column("dia_22", String(5), nullable=True)
    dia_23 = Column("dia_23", String(5), nullable=True)
    dia_24 = Column("dia_24", String(5), nullable=True)
    dia_25 = Column("dia_25", String(5), nullable=True)
    dia_26 = Column("dia_26", String(5), nullable=True)
    dia_27 = Column("dia_27", String(5), nullable=True)
    dia_28 = Column("dia_28", String(5), nullable=True)
    dia_29 = Column("dia_29", String(5), nullable=True)
    dia_30 = Column("dia_30", String(5), nullable=True)
    dia_31 = Column("dia_31", String(5), nullable=True)
