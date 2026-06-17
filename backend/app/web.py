"""Serve o app web (build estático do Expo) com proteção contra path traversal."""

from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import GEMINI_API_KEY, STATIC_DIR, log


def _safe_file(base: Path, rel: str) -> Optional[Path]:
    """Resolve `rel` sob `base` e só retorna se for um arquivo DENTRO de `base`.

    Bloqueia path traversal (ex.: '../../backend/server.py'), pois o caminho
    resolvido precisa permanecer abaixo de `base`.
    """
    if not rel:
        return None
    candidate = (base / rel).resolve()
    try:
        candidate.relative_to(base)
    except ValueError:
        return None
    return candidate if candidate.is_file() else None


def setup_static(app: FastAPI) -> None:
    static_dir = STATIC_DIR
    index_file = static_dir / "index.html"

    if not index_file.is_file():
        log.info("[web] Sem build do frontend em %s — servindo apenas a API", static_dir)

        @app.get("/")
        async def root_info():
            return {"message": "EcoFisioLab API", "status": "running", "ai": bool(GEMINI_API_KEY)}

        return

    log.info("[web] Servindo o app web de %s", static_dir)
    expo_dir = static_dir / "_expo"
    if expo_dir.is_dir():
        app.mount("/_expo", StaticFiles(directory=str(expo_dir)), name="expo-assets")

    # Catch-all (declarado por último → rotas /api/* têm prioridade): serve
    # arquivos estáticos, páginas .html das rotas do Expo Router e, por fim,
    # o index.html (SPA fallback).
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith("api") or full_path.startswith("_expo"):
            raise HTTPException(status_code=404, detail="Not found")
        found = _safe_file(static_dir, full_path) or _safe_file(static_dir, full_path + ".html")
        if found:
            return FileResponse(str(found))
        return FileResponse(str(index_file))
