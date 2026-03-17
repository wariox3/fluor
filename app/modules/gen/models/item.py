from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property
from app.core.tenant_database import Base
from sqlalchemy.orm import relationship

class Item(Base):
    __tablename__ = "gen_item"

    codigo_item_pk = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    