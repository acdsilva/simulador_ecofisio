"""Limitador de requisições simples, por IP e em memória (sem dependências)."""

import time
from collections import defaultdict, deque
from typing import Deque, Dict

from fastapi import HTTPException, Request

from .config import AI_RATE_LIMIT, AI_RATE_WINDOW

_hits: Dict[str, Deque[float]] = defaultdict(deque)


def _client_ip(request: Request) -> str:
    # Atrás de proxy (Render), o IP real vem no X-Forwarded-For.
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


async def ai_rate_limit(request: Request) -> None:
    """Dependência FastAPI: limita chamadas de IA por IP (HTTP 429 ao exceder)."""
    ip = _client_ip(request)
    now = time.monotonic()
    hits = _hits[ip]
    while hits and now - hits[0] > AI_RATE_WINDOW:
        hits.popleft()
    if len(hits) >= AI_RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail="Muitas requisições em pouco tempo. Aguarde um momento e tente novamente.",
        )
    hits.append(now)
    # Evita acúmulo de IPs inativos no dicionário.
    if len(_hits) > 10000:
        for k in [k for k, v in list(_hits.items()) if not v]:
            _hits.pop(k, None)
