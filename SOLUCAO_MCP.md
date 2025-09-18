# 🔧 Solução para Problemas de Instalação do MCP

## ❌ Problema Identificado

Alguns usuários podem enfrentar o erro:
```
ERROR: Could not find a version that satisfies the requirement mcp
ERROR: No matching distribution found for mcp
```

## ✅ Soluções Implementadas

### 1. **Arquivo Alternativo de Dependências**

Criamos `requirements-no-mcp.txt` que contém todas as dependências exceto o MCP:

```bash
# Use este arquivo se tiver problemas com o MCP
pip install -r requirements-no-mcp.txt

# Depois instale o MCP manualmente (opcional)
pip install mcp
```

### 2. **Importação Opcional do MCP**

O código foi modificado para tornar o MCP opcional:

```python
# Importação opcional do MCP
try:
    import mcp
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    logger.warning("MCP (Model Context Protocol) não está disponível. Instale com: pip install mcp")
```

### 3. **Verificação de Disponibilidade**

A função `is_available()` agora verifica se o MCP está instalado:

```python
def is_available(self) -> bool:
    """Verifica se MCP está disponível"""
    return MCP_AVAILABLE and self.config.enabled and bool(self.config.api_key)
```

## 🚀 Como Usar

### Opção 1: Instalação Normal
```bash
pip install -r requirements.txt
```

### Opção 2: Se der erro com MCP
```bash
# Use o arquivo sem MCP
pip install -r requirements-no-mcp.txt

# Instale o MCP separadamente (opcional)
pip install mcp
```

## 📋 O que é o MCP?

O **MCP (Model Context Protocol)** é um SDK da Anthropic que permite:
- Integração avançada com Alpha Vantage
- Acesso a dados financeiros via protocolo estruturado
- Funcionalidades extras de análise financeira

## ⚠️ Impacto da Ausência do MCP

Se o MCP não estiver disponível:
- ✅ A aplicação funciona normalmente
- ✅ Todas as funcionalidades principais mantidas
- ⚠️ Funcionalidades MCP do Alpha Vantage desabilitadas
- ℹ️ Aviso exibido no log sobre MCP não disponível

## 🔍 Verificação de Status

Para verificar se o MCP está funcionando:

```bash
python -c "
try:
    import mcp
    print('✅ MCP disponível:', mcp.__version__)
except ImportError:
    print('❌ MCP não disponível')
"
```

## 🛠️ Troubleshooting

### Problema: Erro de instalação do MCP
**Solução**: Use `requirements-no-mcp.txt`

### Problema: MCP instalado mas não funciona
**Verificação**: 
1. Verifique se `ALPHA_VANTAGE_API_KEY` está configurada
2. Verifique se `ALPHA_VANTAGE_MCP_ENABLED=true` no .env

### Problema: Aplicação não inicia
**Solução**: 
1. Verifique se todas as dependências estão instaladas
2. Use `python main.py --help` para testar

## 📝 Notas Técnicas

- O MCP é opcional e não afeta o funcionamento principal
- A aplicação detecta automaticamente se o MCP está disponível
- Logs informativos são exibidos sobre o status do MCP
- Todas as outras funcionalidades permanecem inalteradas

## 🔄 Atualizações Realizadas

1. ✅ Modificado `src/config/mcp_client.py` para importação opcional
2. ✅ Criado `requirements-no-mcp.txt` como alternativa
3. ✅ Atualizado `README.md` com instruções de troubleshooting
4. ✅ Testado funcionamento com e sem MCP
5. ✅ Verificado compatibilidade com CrewAI 0.186.1

---

**Resultado**: A aplicação agora é mais robusta e funciona em ambientes onde o MCP pode não estar disponível.