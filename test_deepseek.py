#!/usr/bin/env python3
"""
Script para verificar configuração específica do Deepseek
"""

import os
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

def test_deepseek_config():
    """Testa especificamente a configuração do Deepseek"""
    
    print("=== TESTE ESPECÍFICO DEEPSEEK ===")
    print()
    
    # 1. Verificar variáveis de ambiente
    print("1. Variáveis de ambiente relevantes:")
    print(f"DEFAULT_LLM: '{os.getenv('DEFAULT_LLM', 'NÃO DEFINIDO')}'")
    print(f"DEEPSEEK_API_KEY: {'DEFINIDO' if os.getenv('DEEPSEEK_API_KEY') else 'NÃO DEFINIDO'}")
    print(f"DEEPSEEK_MODEL: '{os.getenv('DEEPSEEK_MODEL', 'NÃO DEFINIDO')}'")
    print(f"DEEPSEEK_BASE_URL: '{os.getenv('DEEPSEEK_BASE_URL', 'NÃO DEFINIDO')}'")
    print()
    
    # 2. Testar importação do manager
    print("2. Testando importação do LLM Manager:")
    try:
        from src.config.llm_config import LLMConfigManager, LLMProvider
        print("✓ Importação do LLM Manager: OK")
        
        # Criar nova instância para teste
        manager = LLMConfigManager()
        print(f"✓ Instância criada. Provedor padrão: {manager.default_provider.value}")
        print(f"✓ Provedores disponíveis: {[p.value for p in manager.get_available_providers()]}")
        
    except Exception as e:
        print(f"✗ Erro na importação: {e}")
        return
    
    print()
    
    # 3. Verificar se Deepseek está disponível
    print("3. Verificando disponibilidade do Deepseek:")
    if LLMProvider.DEEPSEEK in manager.configs:
        config = manager.configs[LLMProvider.DEEPSEEK]
        print("✓ Deepseek está configurado")
        print(f"  - Modelo: {config.model}")
        print(f"  - Base URL: {config.base_url}")
        print(f"  - API Key: {'***' if config.api_key else 'NÃO DEFINIDO'}")
        print(f"  - Temperature: {config.temperature}")
        print(f"  - Max Tokens: {config.max_tokens}")
    else:
        print("✗ Deepseek NÃO está configurado")
        return
    
    print()
    
    # 4. Testar obtenção do LLM
    print("4. Testando criação do LLM:")
    try:
        llm = manager.get_crewai_llm(LLMProvider.DEEPSEEK)
        print(f"✓ LLM criado: {type(llm).__name__}")
        
        # Verifica propriedades específicas
        if hasattr(llm, 'model_name'):
            print(f"  - model_name: {llm.model_name}")
        if hasattr(llm, 'model'):
            print(f"  - model: {llm.model}")
        if hasattr(llm, 'openai_api_base'):
            print(f"  - openai_api_base: {llm.openai_api_base}")
            
    except Exception as e:
        print(f"✗ Erro ao criar LLM: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print()
    print("=== TESTE CONCLUÍDO ===")

if __name__ == "__main__":
    test_deepseek_config()