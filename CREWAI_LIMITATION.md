# ⚠️ LIMITAÇÃO IMPORTANTE DO CREWAI

## Problema

O CrewAI possui uma validação rígida que **exige uma chave OpenAI válida**, mesmo quando configurado para usar outros provedores como Deepseek, Anthropic, etc.

## Solução Implementada

O sistema foi configurado para automaticamente adicionar uma chave OpenAI fake caso você não tenha uma real:

```bash
OPENAI_API_KEY=sk-fake-key-for-crewai-validation-only
```

## Como Configurar

### Opção 1: Usar chave OpenAI real (recomendado)
Se você tiver uma chave OpenAI válida, adicione ao `.env`:
```bash
DEFAULT_LLM=deepseek
OPENAI_API_KEY=sua-chave-openai-real
DEEPSEEK_API_KEY=sua-chave-deepseek
# ... outras configurações
```

### Opção 2: Usar chave fake (funcional)
Se não tiver chave OpenAI, o sistema automaticamente adicionará uma fake:
```bash
DEFAULT_LLM=deepseek
# Não definir OPENAI_API_KEY - será adicionada automaticamente
DEEPSEEK_API_KEY=sua-chave-deepseek
# ... outras configurações
```

## O que acontece

1. ✅ O sistema detecta que `DEFAULT_LLM=deepseek`
2. ✅ Adiciona chave OpenAI fake para passar na validação do CrewAI
3. ✅ Configura todos os agentes para usar Deepseek
4. ✅ A chave OpenAI fake nunca é usada para chamadas reais

## Logs esperados

Quando funcionar corretamente, você verá:
```
🔧 Forçando uso do provedor: deepseek
🔧 Adicionada chave OpenAI fake para validação do CrewAI
🔧 LiteL LM configurado para: deepseek/deepseek-reasoner
🔧 Forçando LLM do Crew: ChatOpenAI
✓ LLM do agente: deepseek/deepseek-reasoner
```

## Verificação

Para confirmar que está funcionando:
```bash
python test_llm_quick.py
```

Deve retornar:
```
🎉 CONFIGURAÇÃO OK!
Pode executar: python main.py PETR4.SA
```