#!/bin/bash

# Script de inicialização rápida
set -e

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🚀 CrewAI Stock Analysis - Inicialização Rápida${NC}"

# Verifica se o Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker não está rodando${NC}"
    exit 1
fi

# Verifica se o arquivo .env existe
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  Arquivo .env não encontrado${NC}"
    echo -e "${YELLOW}📝 Copiando .env.example para .env...${NC}"
    cp .env.example .env
    echo -e "${RED}🔑 Configure suas chaves de API no arquivo .env antes de continuar!${NC}"
    exit 1
fi

# Cria diretórios necessários
echo -e "${YELLOW}📁 Criando diretórios...${NC}"
mkdir -p reports logs cache config notebooks

# Build da imagem
echo -e "${YELLOW}🏗️  Fazendo build da imagem Docker...${NC}"
docker-compose build crewai-stock-analysis

echo -e "${GREEN}✅ Inicialização concluída!${NC}"
echo -e "${YELLOW}🎯 Para usar o sistema:${NC}"
echo ""
echo -e "  ${GREEN}# Análise individual${NC}"
echo -e "  docker-compose run --rm crewai-stock-analysis python main.py PETR4.SA"
echo ""
echo -e "  ${GREEN}# Análise em lote${NC}"
echo -e "  docker-compose run --rm crewai-stock-analysis python main.py --batch PETR4.SA VALE3.SA ITUB4.SA"
echo ""
echo -e "  ${GREEN}# Modo interativo${NC}"
echo -e "  docker-compose run --rm crewai-stock-analysis python main.py"
echo ""
echo -e "  ${GREEN}# Jupyter Lab (opcional)${NC}"
echo -e "  docker-compose --profile jupyter up -d"
echo -e "  # Acesse: http://localhost:8888 (token: crewai2024)"
echo ""
echo -e "  ${GREEN}# Com cache Redis (opcional)${NC}"
echo -e "  docker-compose --profile cache up -d"
