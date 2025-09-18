# Makefile para automação de tarefas

.PHONY: help install install-dev test test-cov lint format clean docker-build docker-run docs

# Variáveis
PYTHON := python
PIP := pip
DOCKER_IMAGE := crewai-stock-analysis
DOCKER_TAG := latest

# Cores para output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m # No Color

help: ## Mostra esta ajuda
	@echo "$(GREEN)CrewAI Stock Analysis - Comandos Disponíveis$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Instala dependências de produção
	@echo "$(YELLOW)📦 Instalando dependências de produção...$(NC)"
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)✅ Dependências instaladas!$(NC)"

install-dev: ## Instala dependências de desenvolvimento
	@echo "$(YELLOW)🔧 Instalando dependências de desenvolvimento...$(NC)"
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-dev.txt
	pre-commit install
	@echo "$(GREEN)✅ Ambiente de desenvolvimento configurado!$(NC)"

test: ## Executa testes
	@echo "$(YELLOW)🧪 Executando testes...$(NC)"
	$(PYTHON) -m pytest tests/ -v
	@echo "$(GREEN)✅ Testes concluídos!$(NC)"

test-cov: ## Executa testes com coverage
	@echo "$(YELLOW)📊 Executando testes com coverage...$(NC)"
	$(PYTHON) -m pytest tests/ --cov=src --cov-report=html --cov-report=term
	@echo "$(GREEN)✅ Coverage report gerado em htmlcov/$(NC)"

lint: ## Executa linting
	@echo "$(YELLOW)🔍 Executando linting...$(NC)"
	flake8 src/ main.py
	pylint src/ main.py
	mypy src/ main.py
	@echo "$(GREEN)✅ Linting concluído!$(NC)"

format: ## Formata código
	@echo "$(YELLOW)🎨 Formatando código...$(NC)"
	black src/ main.py tests/
	@echo "$(GREEN)✅ Código formatado!$(NC)"

clean: ## Remove arquivos temporários
	@echo "$(YELLOW)🧹 Limpando arquivos temporários...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ .coverage htmlcov/ .pytest_cache/
	@echo "$(GREEN)✅ Limpeza concluída!$(NC)"

docker-build: ## Constrói imagem Docker
	@echo "$(YELLOW)🐳 Construindo imagem Docker...$(NC)"
	docker build -f docker/Dockerfile -t $(DOCKER_IMAGE):$(DOCKER_TAG) .
	@echo "$(GREEN)✅ Imagem Docker construída!$(NC)"

docker-run: ## Executa container Docker
	@echo "$(YELLOW)🚀 Executando container Docker...$(NC)"
	docker run -it --rm $(DOCKER_IMAGE):$(DOCKER_TAG)

docker-compose-up: ## Inicia todos os serviços
	@echo "$(YELLOW)🚀 Iniciando serviços com Docker Compose...$(NC)"
	docker-compose up -d

docker-compose-down: ## Para todos os serviços
	@echo "$(YELLOW)🛑 Parando serviços...$(NC)"
	docker-compose down

docs: ## Gera documentação
	@echo "$(YELLOW)📚 Gerando documentação...$(NC)"
	mkdocs build
	@echo "$(GREEN)✅ Documentação gerada em site/$(NC)"

docs-serve: ## Serve documentação localmente
	@echo "$(YELLOW)📖 Servindo documentação em http://localhost:8000$(NC)"
	mkdocs serve

analyze: ## Executa análise completa
	@echo "$(YELLOW)🔎 Executando análise completa...$(NC)"
	$(PYTHON) main.py PETR4.SA --type complete

analyze-batch: ## Executa análise em lote
	@echo "$(YELLOW)📊 Executando análise em lote...$(NC)"
	$(PYTHON) main.py --batch PETR4.SA VALE3.SA ITUB4.SA

setup-env: ## Configura arquivo .env
	@if [ ! -f .env ]; then \
		echo "$(YELLOW)📝 Criando arquivo .env...$(NC)"; \
		cp .env.example .env; \
		echo "$(RED)🔑 Configure suas chaves de API no arquivo .env!$(NC)"; \
	else \
		echo "$(GREEN)✅ Arquivo .env já existe!$(NC)"; \
	fi

check: lint test ## Executa todas as verificações

all: clean install-dev format lint test ## Executa pipeline completo

# Comandos de desenvolvimento
dev-install: setup-env install-dev ## Configuração completa para desenvolvimento

dev-test: format lint test-cov ## Pipeline de testes para desenvolvimento

dev-run: ## Executa em modo desenvolvimento
	@echo "$(YELLOW)🔧 Executando em modo desenvolvimento...$(NC)"
	$(PYTHON) main.py --help

# Comandos de produção
prod-build: clean test docker-build ## Build de produção

prod-deploy: prod-build ## Deploy de produção
	@echo "$(YELLOW)🚀 Deploy de produção...$(NC)"
	# Adicione comandos de deploy aqui

# Comandos de utilidades
list-symbols: ## Lista símbolos populares
	$(PYTHON) main.py --list-symbols

interactive: ## Modo interativo
	$(PYTHON) main.py

# Comandos de manutenção
update-deps: ## Atualiza dependências
	@echo "$(YELLOW)📦 Atualizando dependências...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install --upgrade -r requirements.txt
	@echo "$(GREEN)✅ Dependências atualizadas!$(NC)"

security-check: ## Verifica vulnerabilidades
	@echo "$(YELLOW)🔒 Verificando vulnerabilidades...$(NC)"
	safety check
	bandit -r src/
	@echo "$(GREEN)✅ Verificação de segurança concluída!$(NC)"

# Comando padrão
.DEFAULT_GOAL := help
