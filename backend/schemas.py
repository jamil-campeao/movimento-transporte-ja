from pydantic import BaseModel, Field
from typing import Optional, List
import datetime

# Schema para RECEBER dados de um novo anexo do frontend
class AnexoCreate(BaseModel):
    filename: str
    mimetype: str
    dados_base64: str

# Schema para ENVIAR dados de um anexo salvo para o frontend
class Anexo(BaseModel):
    id: int
    filename: str
    mimetype: str
    dados_base64: str
    class Config:
        orm_mode = True


# --- SCHEMAS PARA RELATOS ---

class RelatoBase(BaseModel):
    nome: str
    contato: Optional[str] = None
    instituicao: str
    data_ocorrido: datetime.date 
    relato_texto: str

# 2. CORREÇÃO PRINCIPAL: Este é o schema para o corpo da requisição POST
class RelatoCreatePayload(RelatoBase):
    anexos: List[AnexoCreate] = []

# Schema para ENVIAR um relato completo na resposta da API
class Relato(RelatoBase):
    id: int
    anexos: List[Anexo] = []

    class Config:
        orm_mode = True

class RelatoCreate(RelatoBase):
    pass