# 🌿 EcoFisioLab — Ciências em Contexto

App educacional (mobile + web) para explorar **fisiologia ecológica** por meio de
simulações interativas de espécies dos biomas brasileiros. O aluno escolhe uma espécie,
ajusta as condições ambientais (temperatura, água e alimento) e observa as respostas
fisiológicas em tempo real, com explicações em linguagem acessível.

> Projeto acadêmico — Unipampa (Universidade Federal do Pampa). Uso educacional.

---

## ✨ Funcionalidades

- **Simulador de fisiologia ecológica**: temperatura, disponibilidade de água e de
  alimento como entradas; taxa metabólica, temperatura corporal, probabilidade de
  sobrevivência, gasto energético, nível de estresse e status de homeostase como saídas.
- **Termorregulação**: distingue **reguladores** (endotérmicos) de **conformadores**
  (ectotérmicos).
- **Explicações por IA (opcional)**: integra o Google Gemini quando há chave de API;
  **sem chave, gera explicações educativas localmente** — o app nunca depende de IA externa.
- **Bilíngue**: interface completa em Português e Inglês.

## 🐾 Espécies e biomas (13 espécies, 4 biomas)

| Bioma | Espécies |
|---|---|
| **Pampa** | Capivara, Quero-quero, Preá, Teiú |
| **Amazônia** | Onça-pintada, Arara-azul, Boto-cor-de-rosa |
| **Mata Atlântica** | Mico-leão-dourado, Onça-parda, Preguiça-de-três-dedos |
| **Caatinga** | Veado-catingueiro, Tatu-bola, Asa-branca |

## 🏗️ Arquitetura

**Backend — FastAPI (independente)**
```
GET  /api/species               Lista todas as espécies
GET  /api/species/biome/{biome} Filtra espécies por bioma
GET  /api/species/{id}          Espécie específica (id = slug do nome científico)
GET  /api/biomes                Lista de biomas
POST /api/simulate              Executa a simulação fisiológica
POST /api/explain               Explicação (Gemini se houver chave; senão, local)
```
- Persistência **opcional**: roda em memória por padrão; usa **MongoDB** se `MONGO_URL`
  estiver definido.
- IA **opcional**: usa o SDK oficial `google-generativeai` quando há `GEMINI_API_KEY`.

**Frontend — Expo + React Native (expo-router)**
```
/            Tela inicial e seletor de idioma
/species     Seleção de espécies com filtro por bioma
/simulator   Simulação interativa e resultados
```

## 🚀 Começando

### Pré-requisitos
- Node.js 18+ e npm
- Python 3.11+ (para o backend)
- (Opcional) MongoDB e uma chave do Google Gemini

### 1. Backend
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate   |  Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env        # opcional — funciona sem .env
python server.py              # sobe em http://localhost:8001
```

### 2. Frontend
```bash
cd frontend
npm install
copy .env.example .env        # define EXPO_PUBLIC_BACKEND_URL
npx expo start                # 'w' abre no navegador; ou use o app Expo Go
```

### Variáveis de ambiente
| Onde | Variável | Padrão | Descrição |
|---|---|---|---|
| backend | `GEMINI_API_KEY` | *(vazio)* | Chave do Gemini. Vazio → explicação local. |
| backend | `GEMINI_MODEL` | `gemini-1.5-flash` | Modelo do Gemini. |
| backend | `MONGO_URL` | *(vazio)* | Mongo opcional. Vazio → memória. |
| backend | `DB_NAME` | `ecofisiolab` | Nome do banco (se usar Mongo). |
| backend | `CORS_ORIGINS` | `*` | Origens permitidas (separadas por vírgula). |
| backend | `PORT` | `8001` | Porta do servidor. |
| frontend | `EXPO_PUBLIC_BACKEND_URL` | `http://localhost:8001` | URL do backend. |

## 🧪 Testes do backend
Com o servidor rodando em `http://localhost:8001`:
```bash
python backend_test.py
```

## 🧬 Algoritmo da simulação
As respostas são calculadas a partir de:
1. **Termorregulação** — reguladores mantêm ~37 °C com custo energético; conformadores
   acompanham a temperatura do ambiente.
2. **Estresse térmico** — cresce conforme a temperatura sai da faixa ótima da espécie.
3. **Dependência hídrica** — alta (aquáticas/semiaquáticas), média ou baixa (adaptadas à seca).
4. **Disponibilidade de alimento** — afeta o balanço energético e a sobrevivência.
5. **Saídas** — taxa metabólica, temperatura corporal, sobrevivência, gasto energético,
   nível de estresse e homeostase (estável / estressado / crítico).

## 📦 Publicação
- **Quer só um link para compartilhar (sem instalar nada)?** Siga o
  [PUBLICAR.md](PUBLICAR.md) — passo a passo para publicar tudo como um único serviço
  (app + API + IA) no Render, em ~15 min.
- **Opções avançadas** (web no GitHub Pages, APK Android via EAS, rodar local):
  veja [DEPLOY.md](DEPLOY.md).

> No deploy de serviço único, o backend serve o app web no mesmo endereço, então o app
> chama a API por caminho relativo (`/api`) — sem configurar URLs.

## 📝 Licença e créditos
- Uso educacional. Imagens das espécies: **Wikimedia Commons** (domínio público).
- IA opcional: **Google Gemini**.
- Unipampa — Universidade Federal do Pampa.

---
**Versão:** 1.1.0 · **Status:** funcional e independente de plataforma.
