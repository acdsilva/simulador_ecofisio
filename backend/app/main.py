"""Cria e configura a aplicação FastAPI (CORS, rotas, app web, seed do banco)."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import CORS_ORIGINS
from .routes import router
from .storage import store
from .web import setup_static


@asynccontextmanager
async def lifespan(app: FastAPI):
    await store.init()
    yield


app = FastAPI(title="EcoFisioLab API", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
setup_static(app)  # catch-all do app web por último (rotas /api/* têm prioridade)
