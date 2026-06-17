"""Configuração central via variáveis de ambiente + caminhos e limites."""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger("ecofisiolab")

# Diretório backend/ (pai deste pacote app/). Âncora para arquivos estáticos
# e imagens — assim os caminhos funcionam independentemente do diretório atual.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Banco / IA ---
MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME", "ecofisiolab")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# --- CORS / servidor ---
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()]
PORT = int(os.getenv("PORT", "8001"))

# --- Caminhos ---
STATIC_DIR = Path(os.getenv("STATIC_DIR", str(BASE_DIR.parent / "frontend" / "dist"))).resolve()
IMAGES_DIR = (BASE_DIR / "static_images").resolve()

# --- Limites (proteção contra abuso/custo da IA) ---
AI_RATE_LIMIT = int(os.getenv("AI_RATE_LIMIT", "30"))      # requisições por janela, por IP
AI_RATE_WINDOW = int(os.getenv("AI_RATE_WINDOW", "60"))    # janela em segundos
CHAT_MAX_MESSAGES = int(os.getenv("CHAT_MAX_MESSAGES", "20"))
CHAT_MAX_CHARS = int(os.getenv("CHAT_MAX_CHARS", "2000"))
SIM_HISTORY_MAX = int(os.getenv("SIM_HISTORY_MAX", "500"))  # histórico de simulações em memória
