"""Entrypoint do backend EcoFisioLab.

Mantém compatibilidade: expõe `app` para `uvicorn server:app` (Dockerfile) e
roda direto com `python server.py`. A implementação vive no pacote `app/`.
"""

from app.main import app  # noqa: F401  (reexportado para `uvicorn server:app`)

if __name__ == "__main__":
    import uvicorn

    from app.config import PORT

    uvicorn.run(app, host="0.0.0.0", port=PORT)
