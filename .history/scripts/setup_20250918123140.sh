#!/bin/bash

# Script de configuração e inicialização dos serviços
# Uso: ./scripts/setup.sh

set -e

echo "🚀 Configurando CrewAI Stock Analysis com SearXNG e Browserless"
echo "================================================================"

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não encontrado. Por favor, instale o Docker primeiro."
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose não encontrado. Por favor, instale o Docker Compose primeiro."
    exit 1
fi

# Verificar se arquivo .env existe
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        echo "📝 Criando arquivo .env a partir do .env.example..."
        cp .env.example .env
        echo "✅ Arquivo .env criado. Por favor, edite-o com suas credenciais antes de continuar."
        echo "   Especialmente a ANTHROPIC_API_KEY que é obrigatória."
        echo ""
        read -p "Pressione Enter após configurar o arquivo .env..."
    else
        echo "❌ Arquivo .env.example não encontrado!"
        exit 1
    fi
fi

# Verificar se ANTHROPIC_API_KEY está configurada
if ! grep -q "^ANTHROPIC_API_KEY=sk-" .env; then
    echo "⚠️ ANTHROPIC_API_KEY não parece estar configurada corretamente no .env"
    echo "   Certifique-se de que ela começa com 'sk-ant-'"
    read -p "Continuar mesmo assim? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Criar diretórios necessários
echo "📁 Criando diretórios necessários..."
mkdir -p logs
mkdir -p cache
mkdir -p data

# Build das imagens
echo "🔨 Fazendo build das imagens Docker..."
docker-compose build

# Iniciar serviços
echo "🚀 Iniciando serviços..."
docker-compose up -d searxng browserless

echo "⏳ Aguardando serviços iniciarem (30s)..."
sleep 30

# Testar serviços
echo "🧪 Testando serviços..."
if [ -f scripts/test_services.py ]; then
    python scripts/test_services.py
else
    echo "⚠️ Script de teste não encontrado, testando manualmente..."
    
    # Teste básico do SearXNG
    if curl -s http://localhost:8080 > /dev/null; then
        echo "✅ SearXNG respondendo em http://localhost:8080"
    else
        echo "❌ SearXNG não está respondendo"
    fi
    
    # Teste básico do Browserless
    if curl -s http://localhost:3000/pressure > /dev/null; then
        echo "✅ Browserless respondendo em http://localhost:3000"
    else
        echo "❌ Browserless não está respondendo"
    fi
fi

echo ""
echo "🎉 Configuração concluída!"
echo ""
echo "📋 Próximos passos:"
echo "1. Testar a aplicação: python main.py PETR4.SA"
echo "2. Verificar logs: docker-compose logs -f"
echo "3. Acessar SearXNG: http://localhost:8080"
echo "4. Ver status Browserless: http://localhost:3000/pressure"
echo ""
echo "🛠️ Comandos úteis:"
echo "- Parar serviços: docker-compose down"
echo "- Reiniciar: docker-compose restart"
echo "- Logs: docker-compose logs [serviço]"
echo "- Rebuild: docker-compose build --no-cache"
