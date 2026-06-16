# 📦 Publicação do EcoFisioLab

Duas formas de publicar o app: **web** (GitHub Pages) e **APK Android** (EAS Build).

---

## 🌐 Web — GitHub Pages

O workflow [`.github/workflows/deploy-web.yml`](.github/workflows/deploy-web.yml) faz o
build e publica automaticamente a cada push na branch `main`.

1. Em **Settings → Pages**, defina a fonte como a branch `gh-pages` (criada pelo workflow).
2. Faça push para `main`. O workflow roda `npm ci` + `npx expo export --platform web` e
   publica `frontend/dist`.

> **Base path:** se o site ficar em `https://usuario.github.io/EcoFisioLab/` (GitHub Pages
> de projeto), ajuste em `frontend/app.json` o campo `experiments.baseUrl` para
> `"/EcoFisioLab/"`. Para domínio próprio ou `usuario.github.io` na raiz, mantenha `"/"`.

> **Backend:** a versão web precisa de um backend acessível. Defina
> `EXPO_PUBLIC_BACKEND_URL` (na build) apontando para um backend hospedado (ex.: Render,
> Railway, Fly.io). Sem isso, o app web tenta `http://localhost:8001`.

Build local para testar:
```bash
cd frontend
npm ci
npx expo export --platform web
npx serve dist        # ou qualquer servidor estático
```

---

## 🤖 Android — APK via EAS

O workflow [`.github/workflows/build-android.yml`](.github/workflows/build-android.yml)
roda ao criar uma tag `v*` (ex.: `git tag v1.0.0 && git push --tags`) ou manualmente.

**Pré-requisitos (uma vez):**
1. Conta gratuita em https://expo.dev.
2. Vincular o projeto: `cd frontend && npx eas init` (cria o `projectId`).
3. Gerar um **Access Token** em *Account → Settings → Access tokens* e adicioná-lo em
   **Settings → Secrets and variables → Actions** do repositório como `EXPO_TOKEN`.

O perfil `preview` em [`frontend/eas.json`](frontend/eas.json) gera um **APK** instalável.

Build local (precisa de conta Expo logada):
```bash
cd frontend
npm ci
npx eas build --platform android --profile preview
```

---

## 🖥️ Backend (hospedagem)

O backend é um app FastAPI padrão; basta um host com Python:
```bash
pip install -r backend/requirements.txt
uvicorn server:app --host 0.0.0.0 --port $PORT   # rodando dentro de backend/
```
Defina as variáveis de ambiente conforme o [README](README.md). Para persistência,
informe `MONGO_URL` (ex.: MongoDB Atlas). Para IA, informe `GEMINI_API_KEY`.
