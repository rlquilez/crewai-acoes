#!/bin/bash

# Script para build multi-arquitetura
set -e

# Configurações
IMAGE_NAME="crewai-stock-analysis"
VERSION="1.0.0"
REGISTRY="ghcr.io/rlquilez"  # Ajuste conforme necessário

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Iniciando build multi-arquitetura do CrewAI Stock Analysis${NC}"
echo -e "${YELLOW}📦 Imagem: ${IMAGE_NAME}:${VERSION}${NC}"

# Verifica se buildx está disponível
if ! docker buildx version > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker buildx não está disponível${NC}"
    echo -e "${YELLOW}💡 Execute: docker buildx create --use${NC}"
    exit 1
fi

# Cria builder multi-arquitetura se não existir
if ! docker buildx ls | grep -q "multiarch"; then
    echo -e "${YELLOW}🔧 Criando builder multi-arquitetura...${NC}"
    docker buildx create --name multiarch --driver docker-container --use
    docker buildx inspect --bootstrap
fi

# Build para múltiplas arquiteturas
echo -e "${YELLOW}🏗️  Fazendo build para amd64 e arm64...${NC}"
docker buildx build \
    --platform linux/amd64,linux/arm64 \
    --file docker/Dockerfile \
    --tag ${IMAGE_NAME}:${VERSION} \
    --tag ${IMAGE_NAME}:latest \
    --push \
    .

echo -e "${GREEN}✅ Build multi-arquitetura concluído com sucesso!${NC}"
echo -e "${YELLOW}📥 Para usar a imagem:${NC}"
echo -e "   docker pull ${IMAGE_NAME}:${VERSION}"
echo -e "   docker run -it ${IMAGE_NAME}:${VERSION}"
