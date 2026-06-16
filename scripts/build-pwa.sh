#!/bin/bash

# 🌐 Script de Build PWA para EcoFisioLab
# Este script gera os arquivos estáticos para web

echo "🌿 EcoFisioLab - Build PWA"
echo "=========================="
echo ""

# Navegar para o diretório frontend
cd /app/frontend

echo "📦 Instalando dependências..."
yarn install

echo ""
echo "🔨 Buildando para web..."
npx expo export:web

echo ""
echo "✅ Build completo!"
echo ""
echo "📁 Arquivos gerados em: /app/frontend/dist"
echo ""
echo "🚀 Próximos passos:"
echo ""
echo "  Opção 1 - Vercel (Recomendado):"
echo "  $ cd dist"
echo "  $ vercel"
echo ""
echo "  Opção 2 - Netlify:"
echo "  $ cd dist"
echo "  $ netlify deploy --prod"
echo ""
echo "  Opção 3 - GitHub Pages:"
echo "  Copie o conteúdo de 'dist' para a branch gh-pages"
echo ""
echo "  Opção 4 - Servidor local para teste:"
echo "  $ cd dist"
echo "  $ python3 -m http.server 8080"
echo "  Abra: http://localhost:8080"
echo ""
