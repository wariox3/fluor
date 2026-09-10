from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from app.core.tenant_database import Base
from app.modules.gen.models.tercero import Tercero
from app.modules.tte.models.producto import Producto


class TerceroProducto(Base):
    __tablename__ = "tte_tercero_producto"

    codigo_tercero_producto_pk = Column(Integer, primary_key=True, index=True)
    codigo_tercero_fk = Column(Integer, ForeignKey("gen_tercero.codigo_tercero_pk"), nullable=True)
    codigo_producto_fk = Column(String(20), ForeignKey("tte_producto.codigo_producto_pk"), nullable=True)

    tercero = relationship(Tercero, foreign_keys=[codigo_tercero_fk], backref="terceros_productos_tercero_rel")
    producto = relationship(Producto, foreign_keys=[codigo_producto_fk], backref="terceros_productos_producto_rel")

    @hybrid_property
    def tercero_nombre(self):
        return self.tercero.nombre_corto if self.tercero else None

    @hybrid_property
    def producto_nombre(self):
        return self.producto.nombre if self.producto else None
