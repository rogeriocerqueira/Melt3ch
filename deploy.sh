#!/bin/bash
# MelT3ch — Script de deploy no VPS
# Uso: ./deploy.sh

set -e

echo "🍯 MelT3ch Deploy — iniciando..."

# 1. Verifica dependências
command -v docker >/dev/null 2>&1 || { echo "❌ Docker não instalado"; exit 1; }
command -v docker compose >/dev/null 2>&1 || { echo "❌ Docker Compose não instalado"; exit 1; }

# 2. Verifica .env
if [ ! -f .env ]; then
    echo "❌ Arquivo .env não encontrado"
    echo "   Copie .env.example para .env e configure as variáveis"
    exit 1
fi

# 3. Verifica SECRET_KEY
source .env
if [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" = "troque_isso_em_producao_use_openssl_rand_hex_32" ]; then
    echo "⚠  Gerando SECRET_KEY segura..."
    NEW_KEY=$(openssl rand -hex 32)
    sed -i "s|SECRET_KEY=.*|SECRET_KEY=$NEW_KEY|" .env
    echo "✅ SECRET_KEY gerada e salva no .env"
fi

# 4. Build e sobe os serviços
echo "🔨 Building containers..."
docker compose -f docker-compose.prod.yml --env-file .env build

echo "🚀 Subindo serviços..."
docker compose -f docker-compose.prod.yml --env-file .env up -d

# 5. Aguarda backend
echo "⏳ Aguardando backend..."
sleep 10
for i in $(seq 1 12); do
    if curl -sf http://localhost/health > /dev/null 2>&1; then
        echo "✅ Backend respondendo"
        break
    fi
    echo "   Tentativa $i/12..."
    sleep 5
done

# 6. Status
echo ""
echo "══════════════════════════════════════"
echo "🍯 MelT3ch rodando!"
echo ""
echo "   Frontend:  http://$(hostname -I | awk '{print $1}')"
echo "   API Docs:  http://$(hostname -I | awk '{print $1}')/docs"
echo "   Rastreio:  http://$(hostname -I | awk '{print $1}')/#/rastreio/LT-2026-047"
echo ""
echo "   Login:     daiane@melt3ch.com"
echo "   Senha:     melt3ch2026"
echo "══════════════════════════════════════"

docker compose -f docker-compose.prod.yml ps
