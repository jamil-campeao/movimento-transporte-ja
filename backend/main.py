# main.py
from fastapi import FastAPI, File, UploadFile, Form, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import Optional, List
import models
import schemas
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Relatos - Transporte Público FW",
    description="API para receber e armazenar relatos dos usuários sobre o transporte público."
)


@app.post("/relatos/", response_model=schemas.Relato, status_code=201)
async def criar_relato(
    db: Session = Depends(get_db),
    nome: str = Form(...),
    relato_texto: str = Form(...),
    contato: Optional[str] = Form(None),
    anexo: Optional[UploadFile] = File(None)
):
    """
    Cria um novo relato, salvando o anexo diretamente no banco de dados.
    """
    dados_do_anexo = None
    nome_do_anexo = None
    mimetype_do_anexo = None

    if anexo:
        # Lê os bytes do arquivo enviado
        dados_do_anexo = await anexo.read()
        nome_do_anexo = anexo.filename
        mimetype_do_anexo = anexo.content_type

    db_relato = models.Relato(
        nome=nome,
        contato=contato,
        relato_texto=relato_texto,
        anexo_dados=dados_do_anexo,
        anexo_filename=nome_do_anexo,
        anexo_mimetype=mimetype_do_anexo
    )
    
    db.add(db_relato)
    db.commit()
    db.refresh(db_relato)
    return db_relato

# Rota para listar todos os relatos (sem os dados das imagens)
@app.get("/relatos/", response_model=List[schemas.Relato])
def listar_relatos(db: Session = Depends(get_db)):
    relatos = db.query(models.Relato).all()
    return relatos

@app.get("/relatos/{relato_id}/anexo")
async def obter_anexo_do_relato(relato_id: int, db: Session = Depends(get_db)):
    """
    Busca um relato pelo ID e retorna seu anexo como uma resposta de imagem.
    """
    db_relato = db.query(models.Relato).filter(models.Relato.id == relato_id).first()

    if not db_relato:
        raise HTTPException(status_code=404, detail="Relato não encontrado")
    
    if not db_relato.anexo_dados or not db_relato.anexo_mimetype:
        raise HTTPException(status_code=404, detail="Este relato não possui anexo")

    # Retorna os dados binários com o tipo de conteúdo correto para o navegador
    return Response(content=db_relato.anexo_dados, media_type=db_relato.anexo_mimetype)


@app.get("/")
def root():
    return {"message": "API de Relatos do Transporte Público de FW está no ar!"}