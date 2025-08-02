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
    db: Session = Depends(get_db),
    nome: str = Form(...),
    relato_texto: str = Form(...),
    contato: Optional[str] = Form(None),
    anexos: List[UploadFile] = File(None),
    instituicao: str = Form(...),
    data_ocorrido: datetime.date = Form(...),
    api_key: str = Depends(get_api_key)
):
    """
    Cria um novo relato, salvando o anexo diretamente no banco de dados.
    """

    db_relato = models.Relato(
        nome=nome,
        contato=contato,
        instituicao=instituicao,
        data_ocorrido=data_ocorrido,
        relato_texto=relato_texto,
    )

    db.add(db_relato)
    db.commit()
    db.refresh(db_relato)

    if anexos:
        for anexo_file in anexos:
            dados_do_anexo = await anexo_file.read()
            
            db_anexo = models.Anexo(
                filename=anexo_file.filename,
                mimetype=anexo_file.content_type,
                dados=dados_do_anexo,
                relato_id=db_relato.id  # <-- Vincula o anexo ao ID do relato criado
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
    Retorna os 7 relatos mais recentes, já incluindo seus anexos.
    """
    relatos = (
        db.query(models.Relato)
        .options(joinedload(models.Relato.anexos)) # <-- Carrega os anexos na mesma consulta
        .order_by(models.Relato.id.desc())         # <-- Ordena do mais novo para o mais antigo
        .limit(7)                                  # <-- Limita o resultado a 7 registros
        .all()                                     # <-- Executa a consulta
    )
    return relatos

# @app.get("/relatos/{relato_id}/anexo")
# async def obter_anexo_do_relato(relato_id: int, db: Session = Depends(get_db),
#                                 api_key: str = Depends(get_api_key)
# ):
#     """
#     Busca um relato pelo ID e retorna seu anexo como uma resposta de imagem.
#     """
#     db_relato = db.query(models.Relato).filter(models.Relato.id == relato_id).first()

#     if not db_relato:
#         raise HTTPException(status_code=404, detail="Relato não encontrado")
    
#     if not db_relato.anexo_dados or not db_relato.anexo_mimetype:
#         raise HTTPException(status_code=404, detail="Este relato não possui anexo")

#     # Retorna os dados binários com o tipo de conteúdo correto para o navegador
#     return Response(content=db_relato.anexo_dados, media_type=db_relato.anexo_mimetype)


@app.get("/")
def root():
    return {"message": "API de Relatos do Transporte Público de FW está no ar!"}