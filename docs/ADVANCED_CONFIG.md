# Guia de Configuração Avançada - CrewAI Stock Analysis

## 🎯 Visão Geral das Opções

O sistema suporta múltiplos provedores para máxima flexibilidade:

### 🤖 **Provedores de LLM Suportados**
- **OpenAI GPT-4** (Padrão) - Melhor custo-benefício
- **Anthropic Claude** - Análises mais detalhadas 
- **Deepseek Reasoner** - Raciocínio complexo
- **Grok (X.AI)** - Modelo mais recente
- **Ollama** - Execução local/privada

### 🔍 **Provedores de Busca Suportados**
- **SearXNG** (Padrão) - Privacy-focused, self-hosted
- **Google Custom Search** - Fallback robusto
- **SerpAPI** - Alternativa premium

### 📊 **Fontes de Dados Financeiros**
- **Yahoo Finance** - Sempre ativo, gratuito
- **Alpha Vantage** - Dados aprimorados + MCP support

## 🚀 Configuração Rápida

### Opção 1: Configuração Mínima (OpenAI)
```bash
# Apenas configure OpenAI para começar
DEFAULT_LLM=openai
OPENAI_API_KEY=sk-proj-XXXXXXXX
```

### Opção 2: Configuração Completa Premium
```bash
# LLM: Multiple providers
DEFAULT_LLM=openai
OPENAI_API_KEY=sk-proj-XXXXXXXX
ANTHROPIC_API_KEY=sk-ant-api03-XXXXXXXX
DEEPSEEK_API_KEY=sk-XXXXXXXX

# Search: Multiple providers
DEFAULT_SEARCH_PROVIDER=searxng
GOOGLE_API_KEY=XXXXXXXX
SERPAPI_KEY=XXXXXXXX

# Financial Data: Enhanced
ALPHA_VANTAGE_API_KEY=XXXXXXXX
ALPHA_VANTAGE_ENABLED=true
```

## 🎛️ Configurações Avançadas

### Configuração por Provedor LLM

#### OpenAI (GPT-4)
```bash
OPENAI_API_KEY=sk-proj-XXXXXXXX
OPENAI_MODEL=gpt-4o                 # ou gpt-4-turbo
OPENAI_TEMPERATURE=0.1              # 0-2, criatividade
OPENAI_MAX_TOKENS=4000              # limite de tokens
```

#### Anthropic (Claude)
```bash
ANTHROPIC_API_KEY=sk-ant-api03-XXXXXXXX
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
ANTHROPIC_TEMPERATURE=0.1
ANTHROPIC_MAX_TOKENS=4000
```

#### Deepseek (Reasoner)
```bash
DEEPSEEK_API_KEY=sk-XXXXXXXX
DEEPSEEK_MODEL=deepseek-reasoner    # Para raciocínio complexo
DEEPSEEK_TEMPERATURE=0.1
```

#### Ollama (Local)
```bash
OLLAMA_MODEL=llama3.2:latest        # ou outro modelo local
OLLAMA_BASE_URL=http://localhost:11434
```

### Configuração por Provedor de Busca

#### SearXNG (Privacy-focused)
```bash
SEARXNG_URL=http://searxng:8080
SEARXNG_LANGUAGE=pt-BR
SEARXNG_SAFE_SEARCH=0
SEARXNG_TIMEOUT=30
```

#### Google Custom Search
```bash
GOOGLE_API_KEY=XXXXXXXX
GOOGLE_CSE_ID=XXXXXXXX
GOOGLE_TIMEOUT=10
GOOGLE_MAX_RESULTS=10
```

#### SerpAPI (Premium)
```bash
SERPAPI_KEY=XXXXXXXX
SERPAPI_TIMEOUT=10
SERPAPI_MAX_RESULTS=10
```

### Alpha Vantage (Dados Financeiros Aprimorados)

#### Conta Gratuita
```bash
ALPHA_VANTAGE_API_KEY=XXXXXXXX
ALPHA_VANTAGE_ENABLED=true
ALPHA_VANTAGE_PREMIUM=false
```

#### Conta Premium
```bash
ALPHA_VANTAGE_API_KEY=XXXXXXXX
ALPHA_VANTAGE_ENABLED=true
ALPHA_VANTAGE_PREMIUM=true         # Acesso a mais relatórios
```

## 🔄 Fallback e Redundância

### Estratégia de LLM
1. **Primário**: Provedor configurado em `DEFAULT_LLM`
2. **Fallback**: Se primário falhar, tenta outros configurados
3. **Ordem de prioridade**: OpenAI → Anthropic → Deepseek → Grok → Ollama

### Estratégia de Busca
1. **Primário**: SearXNG (privacy-focused)
2. **Fallback 1**: Google Custom Search
3. **Fallback 2**: SerpAPI

### Dados Financeiros
1. **Base**: Yahoo Finance (sempre ativo)
2. **Enhancement**: Alpha Vantage (quando configurado)
3. **Validação**: Comparação cruzada entre fontes

## 🎯 Casos de Uso Específicos

### Para Análise Individual/Hobby
```bash
DEFAULT_LLM=openai
OPENAI_API_KEY=sk-proj-XXXXXXXX
# SearXNG via Docker (incluído)
# Yahoo Finance (gratuito)
```

### Para Uso Profissional
```bash
# Múltiplos LLMs para comparação
DEFAULT_LLM=openai
OPENAI_API_KEY=sk-proj-XXXXXXXX
ANTHROPIC_API_KEY=sk-ant-api03-XXXXXXXX

# Múltiplas fontes de busca
GOOGLE_API_KEY=XXXXXXXX
SERPAPI_KEY=XXXXXXXX

# Dados financeiros completos
ALPHA_VANTAGE_API_KEY=XXXXXXXX
ALPHA_VANTAGE_ENABLED=true
ALPHA_VANTAGE_PREMIUM=true
```

### Para Máxima Privacidade
```bash
# Ollama local
DEFAULT_LLM=ollama
OLLAMA_MODEL=llama3.2:latest

# Apenas SearXNG (self-hosted)
DEFAULT_SEARCH_PROVIDER=searxng

# Apenas Yahoo Finance (sem APIs externas)
ALPHA_VANTAGE_ENABLED=false
```

## 🔧 Troubleshooting

### Problema: LLM não responde
```bash
# Verifique configuração
python -c "from src.config import validate_config; print(validate_config())"

# Teste conexão específica
python -c "from src.config import get_llm; llm = get_llm(); print('OK')"
```

### Problema: Busca falha
```bash
# Liste provedores disponíveis
python -c "from src.config.search_config import list_available_search_providers; print(list_available_search_providers())"
```

### Problema: Alpha Vantage sem dados
```bash
# Verifique quota/limites
python -c "from src.config.alpha_vantage_config import is_alpha_vantage_available; print(is_alpha_vantage_available())"
```

## 📊 Monitoramento e Logs

### Habilitar Debug Detalhado
```bash
DEBUG=true
LOG_LEVEL=DEBUG
```

### Verificar Status de Configuração
```bash
python -c "
from src.config import get_config_summary
import json
print(json.dumps(get_config_summary(), indent=2))
"
```

## 🎁 Recursos Especiais

### MCP (Model Context Protocol) com Alpha Vantage
- Suporte automático quando Alpha Vantage configurado
- Documentação: https://mcp.alphavantage.co/
- Dados estruturados para análise avançada

### Cache e Performance
```bash
CACHE_ENABLED=true
CACHE_TTL=3600                 # 1 hora
MAX_EXECUTION_TIME=300         # 5 minutos max
```

### Rate Limiting
```bash
MAX_SEARCH_RESULTS=10
SCRAPING_TIMEOUT=30
REQUEST_TIMEOUT=30
```
