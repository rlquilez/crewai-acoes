# Multi-stage build para otimizar imagem
FROM python:3.11-slim as builder

# Define argumentos de build
ARG TARGETPLATFORM
ARG BUILDPLATFORM

# Metadados da imagem
LABEL maintainer="CrewAI Stock Analysis Team"
LABEL description="Sistema avançado de análise de ações usando CrewAI"
LABEL version="1.0.0"

# Configura variáveis de ambiente para Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Cria usuário não-root
RUN useradd --create-home --shell /bin/bash crewai

# Cria diretórios de trabalho
WORKDIR /app

# Copia e instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage de produção
FROM python:3.11-slim as production

# Configura variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_ENV=production \
    REPORTS_DIR=/app/reports \
    LOGS_DIR=/app/logs \
    CACHE_DIR=/app/cache

# Instala dependências runtime
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Cria usuário não-root
RUN useradd --create-home --shell /bin/bash crewai

# Cria estrutura de diretórios
RUN mkdir -p /app/reports /app/logs /app/cache /app/src /app/docker

# Copia dependências do builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copia código da aplicação
COPY src/ /app/src/
COPY main.py /app/
COPY .env.example /app/

# Define ownership dos arquivos
RUN chown -R crewai:crewai /app

# Muda para usuário não-root
USER crewai

# Define diretório de trabalho
WORKDIR /app

# Expõe porta (se necessário para APIs futuras)
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Comando padrão
CMD ["python", "main.py", "--help"]
