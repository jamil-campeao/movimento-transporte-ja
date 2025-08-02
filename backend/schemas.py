# schemas.py
from pydantic import BaseModel
from typing import Optional

class RelatoBase(BaseModel):
    nome: str
    contato: Optional[str] = None
    relato_texto: str

class RelatoCreate(RelatoBase):
    pass

class Relato(RelatoBase):
    id: int
    anexo_filename: Optional[str] = None # Informa o nome do arquivo, se existir
    anexo_mimetype: Optional[str] = None # Informa o tipo do arquivo

    class Config:
        orm_mode = True