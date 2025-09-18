# Correção da Limitação de Dados Históricos - yfinance_tools

## Problema Identificado
O sistema estava limitando os dados históricos a apenas 10 períodos, causando erro ao tentar calcular médias móveis de 20, 50 ou 200 períodos.

## Correções Implementadas

### 1. Nova Função: `obter_precos_historicos`
- **Localização**: `src/tools/yfinance_tools.py`
- **Propósito**: Obter lista de preços históricos sem limitação de 10 períodos
- **Parâmetros**:
  - `symbol`: Símbolo da ação (ex: PETR4.SA)
  - `period`: Período dos dados (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max) - padrão: "6mo"
  - `max_points`: Número máximo de pontos retornados - padrão: 250
- **Retorna**: Lista de preços de fechamento (float)

### 2. Função Modificada: `obter_ultimas_cotacoes`
- **Mudança**: Adicionado parâmetro `limit_display` para controlar quantos registros são mostrados
- **Mantém compatibilidade**: Padrão continua sendo 10 registros para não quebrar funcionalidades existentes

### 3. Atualização dos Agentes
- **Arquivo**: `src/agents/market_agents.py`
- **Mudança**: Adicionada nova ferramenta `obter_precos_historicos` à lista `common_tools`
- **Resultado**: Agentes agora têm acesso à ferramenta que retorna dados suficientes para cálculos técnicos

## Como Usar

### Para Obter Preços para Cálculos Técnicos:
```python
# Obter preços históricos suficientes para MA200
precos = obter_precos_historicos("PETR4.SA", period="1y", max_points=250)

# Calcular média móvel de 200 períodos
ma200 = calculate_moving_average(precos, window=200)
```

### Para Obter Cotações para Visualização:
```python
# Usar função original (mostra apenas últimos 10 por padrão)
cotacoes = obter_ultimas_cotacoes("PETR4.SA", period="1mo")

# Ou configurar para mostrar mais registros
cotacoes = obter_ultimas_cotacoes("PETR4.SA", period="1mo", limit_display=20)
```

## Ferramentas Disponíveis para Agentes

Os agentes CrewAI agora têm acesso a:

1. **`obter_ultimas_cotacoes`** - Para visualizar cotações recentes formatadas
2. **`obter_precos_historicos`** - Para obter dados brutos para cálculos técnicos
3. **`calculate_moving_average`** - Para calcular médias móveis
4. **`calculate_rsi`** - Para calcular RSI
5. **`calculate_support_resistance`** - Para identificar suporte/resistência

## Exemplo de Fluxo Corrigido

**Antes (com erro):**
```
1. Agente chama obter_ultimas_cotacoes → Recebe 10 preços
2. Agente tenta calculate_moving_average(precos, 20) → ERRO: Necessário 20 preços
```

**Depois (funcional):**
```
1. Agente chama obter_precos_historicos("PETR4.SA", "3mo", 50) → Recebe 50+ preços
2. Agente chama calculate_moving_average(precos, 20) → ✅ Sucesso
```

## Benefícios

1. **Cálculos técnicos funcionais**: Médias móveis de qualquer período agora funcionam
2. **Flexibilidade**: Possível obter de 1 dia até dados históricos máximos
3. **Compatibilidade**: Funcionalidades existentes continuam funcionando
4. **Performance**: Controle do número de pontos evita sobrecarga desnecessária

## Testing

Para testar se a correção funciona:

1. Execute uma análise técnica
2. Verifique se o agente consegue calcular MA20, MA50, MA200 sem erros
3. Confirme que os dados retornados são suficientes para os cálculos solicitados