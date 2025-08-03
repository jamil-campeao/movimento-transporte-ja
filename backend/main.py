# main.py
from fastapi import FastAPI, File, UploadFile, Form, Depends, HTTPException, Response, Security
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
import models
import schemas
from database import engine, get_db
import os
import secrets
from dotenv import load_dotenv
import datetime
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

load_dotenv()

models.Base.metadata.create_all(bind=engine)

API_KEY_SECRET = os.getenv("API_KEY")

if not API_KEY_SECRET:
    raise Exception("API_KEY not found in .env file")

# Define o nome do cabeçalho que o cliente deve enviar
API_KEY_NAME = "token"


# Cria o esquema de segurança que o FastAPI usará para extrair a chave
api_key_header_auth = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

async def get_api_key(api_key: str = Security(api_key_header_auth)):
    """Verifica se a chave de API enviada no cabeçalho é válida."""
    # Usamos `secrets.compare_digest` para uma comparação segura contra ataques de tempo
    if not secrets.compare_digest(api_key, API_KEY_SECRET):
        raise HTTPException(
            status_code=403,
            detail="Acesso negado: Chave de API inválida ou ausente."
        )

app = FastAPI(
    title="API de Relatos - Transporte Público FW",
    description="API para receber e armazenar relatos dos usuários sobre o transporte público."
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/relatos/", response_model=schemas.Relato, status_code=201)
async def criar_relato(
    payload: schemas.RelatoCreatePayload,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key)
):
    """
    Cria um novo relato, salvando o anexo diretamente no banco de dados.
    """

    db_relato = models.Relato(
        nome=payload.nome,
        contato=payload.contato,
        instituicao=payload.instituicao,
        data_ocorrido=payload.data_ocorrido,
        relato_texto=payload.relato_texto,
    )
    db.add(db_relato)
    db.commit()
    db.refresh(db_relato)

    if payload.anexos:
        for anexo_data in payload.anexos:
            db_anexo = models.Anexo(
                filename=anexo_data.filename,
                mimetype=anexo_data.mimetype,
                dados=anexo_data.dados,
                relato_id=db_relato.id
            )
            db.add(db_anexo)
    
    db.commit()
    db.refresh(db_relato)
    
    return db_relato

# Rota para listar todos os relatos (sem os dados das imagens)
@app.get("/relatos/all", response_model=List[schemas.Relato])
def listar_todos_relatos(db: Session = Depends(get_db),
                   api_key: str = Depends(get_api_key)
):
    relatos = db.query(models.Relato).all()
    return relatos


@app.get("/relatos/newest", response_model=List[schemas.Relato])
def listar_ultimos_relatos(db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    """
    Retorna os 5 relatos mais recentes, já incluindo seus anexos.
    """
    relatos = (
        db.query(models.Relato)
        .options(joinedload(models.Relato.anexos)) # <-- Carrega os anexos na mesma consulta
        .order_by(models.Relato.id.desc())         # <-- Ordena do mais novo para o mais antigo
        .limit(5)                                  # <-- Limita o resultado a 5 registros
        .all()                                     # <-- Executa a consulta
    )
    return relatos


@app.get("/")
def root():
    return {"message": "API de Relatos do Transporte Público de FW está no ar!"}