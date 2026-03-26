from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property
from app.core.tenant_database import Base
from sqlalchemy.orm import relationship
from app.modules.gen.models.impuesto import Impuesto

class Item(Base):
    __tablename__ = "gen_item"

    codigo_item_pk = Column(Integer, primary_key=True, index=True)
    codigo_impuesto_retencion_fk = Column(String(5), ForeignKey("gen_impuesto.codigo_impuesto_pk"))
    codigo_impuesto_retencion_compra_fk = Column(String(5), ForeignKey("gen_impuesto.codigo_impuesto_pk"))
    codigo_impuesto_iva_venta_fk = Column(String(5), ForeignKey("gen_impuesto.codigo_impuesto_pk"))
    codigo_impuesto_iva_compra_fk = Column(String(5), ForeignKey("gen_impuesto.codigo_impuesto_pk"))
    nombre = Column(String)
    afecta_inventario = Column(Boolean, default=True)
    producto = Column(Boolean, default=False)
    servicio = Column(Boolean, default=False)
    venta = Column(Boolean, default=False)
    compra = Column(Boolean, default=False)
    codigo_empresa_fk = Column(Integer)
    
    impuesto_retencion = relationship(Impuesto, foreign_keys=[codigo_impuesto_retencion_fk],backref="items_retencion")
    impuesto_retencion_compra = relationship(Impuesto,foreign_keys=[codigo_impuesto_retencion_compra_fk],backref="items_retencion_compra")
    impuesto_iva_venta = relationship(Impuesto,foreign_keys=[codigo_impuesto_iva_venta_fk],backref="items_iva")
    impuesto_iva_compra = relationship(Impuesto,foreign_keys=[codigo_impuesto_iva_compra_fk],backref="items_iva_compra")