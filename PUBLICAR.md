# 🚀 Como publicar o EcoFisioLab (passo a passo, sem saber programar)

No fim você terá **um link** (ex.: `https://ecofisiolab.onrender.com`) que qualquer
pessoa abre no **celular ou computador, sem instalar nada**. A explicação por IA
(Google Gemini) funciona porque a chave fica guardada no servidor, em segurança.

Você faz isto **uma única vez**. Tempo estimado: ~15 minutos. Tudo é gratuito.

---

## Passo 1 — Pegar a chave do Google Gemini (grátis)

1. Acesse **https://aistudio.google.com/apikey** e entre com sua conta Google.
2. Clique em **“Create API key”** (Criar chave de API).
3. **Copie** o código que aparecer (algo como `AIza...`) e guarde — vamos usar no Passo 4.

## Passo 2 — Colocar o projeto no GitHub

1. Crie uma conta grátis em **https://github.com** (se ainda não tiver).
2. Clique no **+** (canto superior direito) → **New repository**.
3. Dê um nome (ex.: `ecofisiolab`), deixe **Public**, e clique em **Create repository**.
4. Na página do repositório vazio, clique em **“uploading an existing file”**.
5. **Arraste para a página o conteúdo da pasta do projeto** (a pasta interna
   `EcoFisioLab-main`, aquela que contém os arquivos `Dockerfile`, `render.yaml`,
   `README.md`, e as pastas `backend` e `frontend`).
   > Importante: arraste o **conteúdo** dessa pasta, não a pasta dentro de outra pasta —
   > o arquivo `Dockerfile` precisa ficar na **raiz** do repositório.
6. Clique em **Commit changes**.

## Passo 3 — Criar o serviço no Render

1. Crie uma conta grátis em **https://render.com** (pode entrar com o GitHub).
2. No painel, clique em **New +** → **Blueprint**.
3. Conecte sua conta do GitHub e **selecione o repositório** `simulador_ecofisio`.
   Quando pedir a **branch**, escolha **`Projeto-1.0`** (é onde está o projeto).
4. O Render vai ler o arquivo `render.yaml` e mostrar o serviço **ecofisiolab**.
   Clique em **Apply** / **Create**.

## Passo 4 — Informar a chave da IA

1. Quando pedir as variáveis de ambiente (ou depois, em **Environment**), adicione:
   - **Key:** `GEMINI_API_KEY`
   - **Value:** *(cole a chave que você copiou no Passo 1)*
2. Salve. O Render vai **construir e publicar** o app (leva alguns minutos na 1ª vez).

## Passo 5 — Compartilhar o link

1. Quando aparecer **“Live”**, copie o endereço no topo da página
   (ex.: `https://ecofisiolab.onrender.com`).
2. **Esse é o link do curso.** Mande para as pessoas — abre direto no navegador. ✅

---

## ❓ Dúvidas comuns

- **“Demorou para abrir na primeira vez.”** No plano **grátis** do Render, o serviço
  “hiberna” após ~15 min sem uso e leva ~30–60 s para acordar no primeiro acesso.
  Depois fica rápido. Para evitar a espera, dá para mudar para o plano pago (~US$ 7/mês)
  em **Settings → Instance Type**.
- **“A explicação por IA não apareceu.”** Confira se a `GEMINI_API_KEY` foi salva
  corretamente (Passo 4). Mesmo sem ela, o app **continua funcionando** com uma
  explicação gerada localmente — só não usa o Gemini.
- **“Quero trocar o modelo da IA.”** Em **Environment**, mude `GEMINI_MODEL`
  (ex.: `gemini-1.5-flash`, `gemini-1.5-pro`).
- **Alternativas ao Render:** Railway, Fly.io ou Hugging Face Spaces também rodam o
  mesmo `Dockerfile`. O Render é o caminho mais simples para começar.

> Detalhes técnicos (rodar local, build manual, GitHub Pages) estão em [DEPLOY.md](DEPLOY.md).
