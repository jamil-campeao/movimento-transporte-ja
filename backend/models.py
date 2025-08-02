# models.py
from sqlalchemy import Column, Integer, String, LargeBinary
from database import Base

class Relato(Base):
    __tablename__ = "relatos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    contato = Column(String, nullable=True)
    relato_texto = Column(String)

    # Campos para o anexo
    anexo_dados = Column(LargeBinary, nullable=True)
    anexo_filename = Column(String, nullable=True)
    anexo_mimetype = Column(String, nullable=True)