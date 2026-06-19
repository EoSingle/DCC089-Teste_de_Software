from fastapi import FastAPI

from app.database import Base, engine
from app.routers import router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CTF Platform",
    description="Motor de Validação de Flags e Pontuação para competições CTF",
    version="1.0.0",
)

app.include_router(router, prefix="/api/v1")


@app.get("/health")
def health_check():
    return {"status": "ok"}
