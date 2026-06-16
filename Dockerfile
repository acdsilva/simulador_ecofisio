# syntax=docker/dockerfile:1

# ============================================================================
# EcoFisioLab — imagem única que serve a API e o app web no mesmo endereço.
# ============================================================================

# --- Estágio 1: build do app web (Expo) ---
FROM node:20-slim AS web
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
# Sem EXPO_PUBLIC_BACKEND_URL → o app usa caminho relativo "/api" (mesmo domínio).
RUN npx expo export --platform web

# --- Estágio 2: backend Python que serve a API + o app web ---
FROM python:3.12-slim
WORKDIR /app
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt
COPY backend/ ./backend/
COPY --from=web /app/frontend/dist ./frontend/dist
WORKDIR /app/backend
EXPOSE 8001
# A maioria das hospedagens (Render, Railway…) injeta a variável PORT.
CMD ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port ${PORT:-8001}"]
