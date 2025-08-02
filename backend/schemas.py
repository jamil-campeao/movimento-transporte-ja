# schemas.py
from pydantic import BaseModel
from typing import Optional, List
import datetime

# Schema para exibir informações de um anexo (sem os dados binários)
class Anexo(BaseModel):
    id: int
    filename: str
    mimetype: str

    class Config:
        orm_mode = True

# Schema base para um relato
class RelatoBase(BaseModel):
    nome: str
    contato: Optional[str] = None
    instituicao: str
    data_ocorrido: datetime.date
    relato_texto: str

class RelatoCreate(RelatoBase):
    pass

# Schema para exibir um relato completo, incluindo a lista de seus anexos
class Relato(RelatoBase):
    id: int
    anexos: List[Anexo] = []  # <--lista de anexos

    class Config:
        orm_mode = True