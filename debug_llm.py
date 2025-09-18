#!/usr/bin/env python3
"""
Script de debug para verificar a configuração de LLM
"""

import os
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

# Carrega o .env file se existir
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv não instalado, usando apenas variáveis de ambiente do sistema")

def debug_llm_config():
    """Debug da configuração de LLM"""
    
    print("=== DEBUG CONFIGURAÇÃO LLM ===")
    print()
    
    # Verifica variáveis de ambiente
    print("1. Variáveis de ambiente:")
    print(f"DEFAULT_LLM: {os.getenv('DEFAULT_LLM', 'NÃO DEFINIDO')}")
    print(f"DEEPSEEK_API_KEY: {'***' if os.getenv('DEEPSEEK_API_KEY') else 'NÃO DEFINIDO'}")
    print(f"DEEPSEEK_MODEL: {os.getenv('DEEPSEEK_MODEL', 'NÃO DEFINIDO')}")
    print(f"DEEPSEEK_BASE_URL: {os.getenv('DEEPSEEK_BASE_URL', 'NÃO DEFINIDO')}")
    print()
    
    # Verifica configuração do LLM Manager
    print("2. LLM Manager:")
    try:
        from src.config.llm_config import llm_manager, LLMProvider
        
        print(f"Provedor padrão: {llm_manager.default_provider.value}")
        print(f"Provedores disponíveis: {[p.value for p in llm_manager.get_available_providers()]}")
        
        # Verifica se Deepseek está disponível
        if LLMProvider.DEEPSEEK in llm_manager.configs:
            deepseek_config = llm_manager.configs[LLMProvider.DEEPSEEK]
            print(f"Deepseek configurado: SIM")
            print(f"Deepseek model: {deepseek_config.model}")
            print(f"Deepseek API key: {'***' if deepseek_config.api_key else 'NÃO DEFINIDO'}")
        else:
            print(f"Deepseek configurado: NÃO")
        
    except Exception as e:
        print(f"Erro ao carregar LLM Manager: {e}")
    
    print()
    
    # Testa obtenção do LLM padrão
    print("3. Teste de obtenção do LLM:")
    try:
        from src.config import get_llm
        
        # Teste sem especificar provedor
        llm_default = get_llm()
        print(f"LLM padrão obtido: {type(llm_default).__name__}")
        
        # Testa especificamente o Deepseek
        llm_deepseek = get_llm('deepseek')
        print(f"LLM Deepseek obtido: {type(llm_deepseek).__name__}")
        
        # Verifica se são o mesmo objeto (deveria ser)
        print(f"São o mesmo LLM: {llm_default is llm_deepseek}")
        
    except Exception as e:
        print(f"Erro ao obter LLM: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_llm_config()