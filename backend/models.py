# models.py
from sqlalchemy import Column, Integer, String, LargeBinary, Date, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Relato(Base):
    __tablename__ = "relatos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    contato = Column(String, nullable=True)
    instituicao = Column(String)
    data_ocorrido = Column(Date)
    relato_texto = Column(String)

    # Relação: Um relato pode ter uma lista de anexos.
    anexos = relationship("Anexo", back_populates="relato")

class Anexo(Base):
    __tablename__ = "anexos"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    mimetype = Column(String)
    dados = Column(LargeBinary)
    
    # Chave estrangeira que liga o anexo ao seu relato correspondente
    relato_id = Column(Integer, ForeignKey("relatos.id"))
    
    # Relação inversa: Um anexo pertence a um relato.
    relato = relationship("Relato", back_populates="anexos")